#!/usr/bin/env python3
"""Hostile tests for the independent conditional n3=60 audit baseline."""

from __future__ import annotations

from collections import Counter
from itertools import combinations
import unittest

import independent_baseline as ib


def circulant(n: int, steps: tuple[int, ...]) -> ib.Adjacency:
    edges = {
        ib.normalize_edge(vertex, (vertex + step) % n)
        for vertex in range(n)
        for step in steps
    }
    return ib.adjacency_from_edges(n, edges)


def cube_graph() -> ib.Adjacency:
    return ib.adjacency_from_edges(
        8,
        (
            (vertex, vertex ^ (1 << bit))
            for vertex in range(8)
            for bit in range(3)
            if vertex < (vertex ^ (1 << bit))
        ),
    )


def two_double_stars() -> ib.Adjacency:
    return ib.adjacency_from_edges(
        12,
        (
            (0, 1),
            (0, 2),
            (0, 3),
            (1, 4),
            (1, 5),
            (6, 7),
            (6, 8),
            (6, 9),
            (7, 10),
            (7, 11),
        ),
    )


class RectangleIdentityTests(unittest.TestCase):
    def test_exhaustive_general_identity_including_repeats(self) -> None:
        self.assertEqual(ib.rectangle_identity_exhaustive(), 17065)

    def test_kronecker_terms_are_essential(self) -> None:
        empty = ib.adjacency_from_edges(3, ())
        exact = ib.rectangle_identity_rhs(empty, 0, 1, 0, 2)
        without_delta = 0
        self.assertEqual(exact, 12)
        self.assertNotEqual(exact, without_delta)

    def test_sign_mutation_is_detected(self) -> None:
        witness_found = False
        for adj in ib.enumerate_simple_graphs(4):
            exact = ib.rectangle_identity_rhs(adj, 0, 1, 2, 3)
            mutated = (
                -ib.edge_indicator(adj, 0, 2)
                - ib.edge_indicator(adj, 0, 3)
                + ib.edge_indicator(adj, 1, 2)
                - ib.edge_indicator(adj, 1, 3)
            )
            if exact != mutated:
                witness_found = True
                break
        self.assertTrue(witness_found)

    def test_adjacent_edge_rectangle_is_perfect_matching(self) -> None:
        self.assertEqual(
            ib.adjacent_edge_rectangle_parameters(),
            {
                "common_neighbors": 1,
                "exclusive_per_side": 12,
                "cross_degree": 1,
                "is_perfect_matching": True,
                "cross_edges": 12,
            },
        )


class ComponentAndCrossingTests(unittest.TestCase):
    def test_complete_component_classification(self) -> None:
        parts = ib.rectangle_component_lengths(24)
        self.assertEqual(len(parts), 11)
        self.assertTrue(all(sum(part) == 24 for part in parts))
        self.assertTrue(all(all(length % 4 == 0 for length in part) for part in parts))
        self.assertIn((4, 4, 4, 4, 4, 4), parts)
        self.assertIn((24,), parts)

    def test_crossing_shapes(self) -> None:
        self.assertEqual(ib.enumerate_crossing_shapes(1, 4), ((0, ()),))
        self.assertEqual(
            ib.enumerate_crossing_shapes(2, 2),
            ((0, ()), (4, (4,))),
        )
        self.assertEqual(
            ib.enumerate_crossing_shapes(2, 3),
            ((0, ()), (4, (4,))),
        )
        self.assertEqual(
            ib.enumerate_crossing_shapes(3, 3),
            ((0, ()), (4, (4,)), (6, (6,))),
        )
        self.assertEqual(
            ib.enumerate_crossing_shapes(4, 4),
            ((0, ()), (4, (4,)), (6, (6,)), (8, (4, 4)), (8, (8,))),
        )

    def test_one_sided_degree_rule_is_rejected(self) -> None:
        # Both rows have degree two, but columns have degrees one, one, two.
        with self.assertRaisesRegex(ValueError, "column degree"):
            ib.crossing_components(2, 3, ((0, 0), (0, 2), (1, 1), (1, 2)))

    def test_six_edge_3_by_3_is_legal_but_not_at_size_two(self) -> None:
        cycle6 = ((0, 0), (0, 1), (1, 1), (1, 2), (2, 2), (2, 0))
        self.assertEqual(ib.crossing_components(3, 3, cycle6), (6,))
        with self.assertRaises(ValueError):
            ib.crossing_components(2, 3, cycle6)


class LocalRefinementTests(unittest.TestCase):
    def setUp(self) -> None:
        self.base = two_double_stars()
        self.base_edges, self.line = ib.line_graph(self.base)
        self.first = self.base_edges.index((0, 1))
        self.second = self.base_edges.index((6, 7))
        self.assertTrue(
            ib.edge_pair_is_induced_matching(
                self.base, self.base_edges[self.first], self.base_edges[self.second]
            )
        )
        self.base_d_edges = {
            ib.normalize_edge(a, b)
            for a, row in enumerate(self.line)
            for b in row
            if a < b
        }
        self.base_d_edges.add(ib.normalize_edge(self.first, self.second))

    def test_cross_base_edge_destroys_induced_matching(self) -> None:
        mutated_edges = [
            (a, b)
            for a, row in enumerate(self.base)
            for b in row
            if a < b
        ]
        mutated_edges.append((0, 6))
        mutated = ib.adjacency_from_edges(12, mutated_edges)
        self.assertFalse(
            ib.edge_pair_is_induced_matching(
                mutated, (0, 1), (6, 7)
            )
        )

    def test_zero_crossing_forbids_all_active_rectangle_edges(self) -> None:
        d = ib.adjacency_from_edges(len(self.base_edges), self.base_d_edges)
        self.assertTrue(
            ib.check_disjoint_point_edge_local(
                self.base, d, self.first, self.second, 0
            )
        )
        self.assertTrue(
            ib.check_disjoint_point_edge_from_meeting(
                self.line, d, self.first, self.second, 0
            )
        )

    def test_positive_crossing_forces_perfect_matching(self) -> None:
        left = sorted(self.line[self.first])
        right = sorted(self.line[self.second])
        edges = set(self.base_d_edges)
        edges.update(ib.normalize_edge(a, b) for a, b in zip(left, right))
        d = ib.adjacency_from_edges(len(self.base_edges), edges)
        self.assertTrue(
            ib.check_disjoint_point_edge_local(
                self.base, d, self.first, self.second, 4
            )
        )
        self.assertTrue(
            ib.check_disjoint_point_edge_from_meeting(
                self.line, d, self.first, self.second, 4
            )
        )

    def test_four_cross_edges_sharing_endpoint_are_not_accepted(self) -> None:
        left = sorted(self.line[self.first])
        right = sorted(self.line[self.second])
        edges = set(self.base_d_edges)
        edges.update(ib.normalize_edge(left[0], b) for b in right)
        d = ib.adjacency_from_edges(len(self.base_edges), edges)
        self.assertFalse(
            ib.check_disjoint_point_edge_local(
                self.base, d, self.first, self.second, 4
            )
        )


class PointFamilyTests(unittest.TestCase):
    def test_triangle_free_cubic_edge_points_pass(self) -> None:
        cube = cube_graph()
        edges, _ = ib.line_graph(cube)
        points = ib.validate_point_family(
            edges,
            8,
            expected_sizes=Counter({2: 12}),
            occurrences_per_label=3,
        )
        self.assertEqual(len(points), 12)

    def test_berge_triangle_is_rejected(self) -> None:
        k4 = ib.adjacency_from_edges(4, combinations(range(4), 2))
        edges, _ = ib.line_graph(k4)
        with self.assertRaisesRegex(ValueError, "Berge triangle"):
            ib.validate_point_family(
                edges,
                4,
                expected_sizes=Counter({2: 6}),
                occurrences_per_label=3,
            )

    def test_duplicate_indexed_point_value_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "duplicate point"):
            ib.validate_point_family(
                ((0, 1), (0, 1)),
                2,
                occurrences_per_label=2,
            )

    def test_two_factor_parser_rejects_missing_degree(self) -> None:
        with self.assertRaisesRegex(ValueError, "degree two"):
            ib.validate_two_factor(4, range(4), ((0, 1), (2, 3)))


class OutsideGramTests(unittest.TestCase):
    def test_residual_a_exact_moments(self) -> None:
        d = circulant(27, (1, 2, 3))
        self.assertTrue(all(len(row) == 6 for row in d))
        self.assertEqual(ib.degree_moment_formula(d, 72), (216, 648))
        gram = ib.outside_gram(d)
        self.assertTrue(all(gram[i][i] == 8 for i in range(27)))
        self.assertTrue(all(sum(row) == 24 for row in gram))

    def test_residual_b_empty_exact_moments(self) -> None:
        d = circulant(30, (1, 2, 3))
        self.assertEqual(ib.degree_moment_formula(d, 69), (240, 900))
        gram = ib.outside_gram(d)
        self.assertTrue(all(sum(row) == 30 for row in gram))

    def test_regular_gram_eigenvalue_polynomial(self) -> None:
        for theta in range(-8, 9):
            value = ib.expected_regular_gram_eigenvalue(30, theta)
            self.assertEqual(value, (3 - theta) * (theta + 4))
            if -4 <= theta <= 3:
                self.assertGreaterEqual(value, 0)
            else:
                self.assertLess(value, 0)
        self.assertEqual(ib.regular_principal_gram_eigenvalue(27), 24)
        self.assertEqual(ib.regular_principal_gram_eigenvalue(30), 30)

    def test_psd_is_not_a_binary_factor_certificate(self) -> None:
        matrix = ((1, 2), (2, 4))
        self.assertEqual(ib.exact_psd(matrix), (True, 1))
        self.assertEqual(
            ib.binary_gram_entry_defects(matrix),
            ((0, 1, "intersection exceeds row weight"),),
        )

    def test_exact_psd_rejects_zero_diagonal_nonzero_row(self) -> None:
        self.assertEqual(ib.exact_psd(((0, 1), (1, 0))), (False, 0))

    def test_binary_factor_is_replayed_not_declared(self) -> None:
        gram = ((1, 1), (1, 1))
        self.assertTrue(ib.verify_binary_factor(gram, ((1, 0), (1, 0))))
        self.assertFalse(ib.verify_binary_factor(gram, ((1, 0), (0, 1))))

    def test_full_block_order_is_checked(self) -> None:
        self.assertIn(
            "order 0 != 99",
            ib.srg_block_defects((), (), ()),
        )


class ZCoverageTests(unittest.TestCase):
    EXPECTED_TYPES = {
        "empty",
        "K2",
        "2K2",
        "P3",
        "3K2",
        "P3 + K2",
        "P4",
        "K1,3",
        "K3",
    }

    def test_all_and_only_nine_z_types(self) -> None:
        types = ib.enumerate_z_types()
        self.assertEqual(len(types), 9)
        self.assertEqual(set(types), self.EXPECTED_TYPES)

    def test_z_moment_and_histogram_table(self) -> None:
        expected = {
            "empty": (0, 0, 240, 900, 1297),
            "K2": (2, 2, 238, 872, 354),
            "2K2": (4, 4, 236, 844, 69),
            "P3": (4, 6, 236, 842, 52),
            "3K2": (6, 6, 234, 816, 6),
            "P3 + K2": (6, 8, 234, 814, 3),
            "P4": (6, 10, 234, 812, 2),
            "K1,3": (6, 12, 234, 810, 1),
            "K3": (6, 12, 234, 810, 1),
        }
        for name, row in expected.items():
            actual = ib.z_moment_row(name)
            self.assertEqual(
                (
                    actual["T"],
                    actual["U"],
                    actual["outside_sum"],
                    actual["outside_square_sum"],
                    actual["histogram_count"],
                ),
                row,
                name,
            )

    def test_type_omission_is_detectable(self) -> None:
        incomplete = self.EXPECTED_TYPES - {"K3"}
        self.assertNotEqual(incomplete, set(ib.enumerate_z_types()))

    def test_moments_do_not_identify_z_type(self) -> None:
        star = ib.z_moment_row("K1,3")
        triangle = ib.z_moment_row("K3")
        self.assertEqual((star["T"], star["U"]), (triangle["T"], triangle["U"]))
        self.assertNotEqual(
            ib.canonical_unlabeled_graph(ib.Z_TYPE_EDGES["K1,3"]),
            ib.canonical_unlabeled_graph(ib.Z_TYPE_EDGES["K3"]),
        )


if __name__ == "__main__":
    unittest.main()
