#!/usr/bin/env python3
"""Unit tests for the Wave 69 discovery implementation."""

from __future__ import annotations

import unittest

import exact_search as subject


class DerivationTests(unittest.TestCase):
    def test_srg_spectrum(self) -> None:
        self.assertEqual(
            subject.derive_srg_eigenvalue_multiplicities(),
            {14: 1, 3: 54, -4: 44},
        )

    def test_fixed_spectrum(self) -> None:
        self.assertEqual(
            subject.derive_fixed_eigenspace_multiplicities(),
            {14: 1, 3: 4, -4: 4},
        )

    def test_all_seven_row_shapes_are_derived(self) -> None:
        self.assertEqual(subject.derive_row_shapes(), subject.EXPECTED_ROW_SHAPES)
        self.assertEqual(
            {key: len(value) for key, value in subject.derive_row_templates().items()},
            {0: 2716, 2: 3360, 4: 28},
        )

    def test_all_three_diagonal_cases_are_derived(self) -> None:
        self.assertEqual(
            subject.derive_diagonal_cases(), subject.EXPECTED_DIAGONALS
        )

    def test_fourier_obstruction_has_no_integral_membership_case(self) -> None:
        obstruction = subject.derive_cayley_fourier_obstruction()
        records = obstruction["S_X_values_by_membership"]
        self.assertEqual(records["0"]["numerator"], -18)
        self.assertEqual(records["1"]["numerator"], 81)
        self.assertFalse(records["0"]["is_integer"])
        self.assertFalse(records["1"]["is_integer"])

    def test_order_11_fixed_point_argument_eliminates_positive_counts(self) -> None:
        result = subject.derive_order_11_fixed_point_obstruction()
        self.assertEqual(result["only_nonidentity_fixed_count"], 0)
        self.assertEqual(result["f_11"]["neighbor_degree_sum"], 9)
        self.assertEqual(result["f_11"]["required_sum"], 20)
        self.assertEqual(
            result["f_22"]["high_neighbors_of_degree_3_vertex"], 3
        )
        self.assertEqual(
            result["f_22"]["high_neighbors_of_degree_14_vertex"], 0
        )
        self.assertEqual(
            result["f_at_least_33"]["neighbor_degree_identity_forces_f"], 99
        )


class SearchTests(unittest.TestCase):
    def test_every_indexed_row_has_the_required_local_equations(self) -> None:
        shapes = subject.derive_row_shapes()
        for diagonal in subject.EXPECTED_DIAGONALS:
            indices = subject.build_prefix_indices(diagonal)
            for vertex, buckets in enumerate(indices):
                for rows in buckets.values():
                    for row in rows:
                        self.assertEqual(row[vertex], diagonal[vertex])
                        self.assertEqual(sum(row), 14)
                        self.assertEqual(
                            sum(value * value for value in row) + row[vertex],
                            34,
                        )
                        off_diagonal = tuple(
                            sorted(
                                value
                                for index, value in enumerate(row)
                                if index != vertex
                            )
                        )
                        self.assertIn(off_diagonal, shapes[diagonal[vertex]])

    def test_canonical_cross_check_has_no_quotient(self) -> None:
        result = subject.generate_results("canonical")
        records = result["searches"]["canonical"]
        self.assertEqual([record["solutions"] for record in records], [0, 0, 0])
        self.assertEqual(result["quotient_candidate_count"], 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
