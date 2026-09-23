#!/usr/bin/env python3
"""Hostile exact tests for the independent Wave 21 local verifier."""

from fractions import Fraction
import unittest

import independent_check as check


class RowProfileTests(unittest.TestCase):
    def test_row_profile_all_q(self) -> None:
        for q in range(13):
            profile = check.row_profile(q)
            self.assertEqual(sum(profile.values()), 212)
            self.assertEqual(sum(r * n for r, n in profile.items()), 216)
            self.assertEqual(
                sum((r * (r - 1) // 2) * n for r, n in profile.items()), 36
            )

    def test_full_row_moments(self) -> None:
        for q in range(13):
            self.assertEqual(check.row_moment(q, 1), 0)
            self.assertEqual(check.row_moment(q, 3), 6 * (q - 2))

    def test_hostile_second_moment_factor(self) -> None:
        # The ordered construction count 72 must be divided by two.
        self.assertNotEqual(72, 36)
        self.assertEqual(
            sum((r * (r - 1) // 2) * n for r, n in check.row_profile(5).items()),
            36,
        )


class TensorTests(unittest.TestCase):
    def test_tensor_gram_index_order_on_toy_vectors(self) -> None:
        vectors = ((1, 0), (1, 1), (0, 2))

        def dot(x, y):
            return sum(a * b for a, b in zip(x, y))

        gram = [[dot(x, y) for y in vectors] for x in vectors]
        hadamard_square = [[entry * entry for entry in row] for row in gram]

        tensors = []
        for i in range(len(vectors)):
            tensor = [[0, 0], [0, 0]]
            for j, vector in enumerate(vectors):
                for a in range(2):
                    for b in range(2):
                        tensor[a][b] += gram[i][j] * vector[a] * vector[b]
            tensors.append(tensor)

        def frobenius(left, right):
            return sum(
                left[a][b] * right[a][b] for a in range(2) for b in range(2)
            )

        for i in range(3):
            for k in range(3):
                direct = frobenius(tensors[i], tensors[k])
                contracted = sum(
                    gram[i][j] * hadamard_square[j][ell] * gram[ell][k]
                    for j in range(3)
                    for ell in range(3)
                )
                self.assertEqual(direct, contracted)

    def test_traceless_norm_and_coefficient(self) -> None:
        self.assertEqual(check.traceless_tensor_norm_squared(), Fraction(172, 11))
        for q in range(13):
            self.assertEqual(check.tensor_coefficient(q), 6 * (q - 2))
            self.assertEqual(
                check.tensor_diagonal_lower(q), Fraction(99, 43) * (q - 2) ** 2
            )

    def test_endpoint_cap_and_allowed_q(self) -> None:
        self.assertEqual(check.endpoint_diagonal_cap(), 88)
        self.assertEqual(check.endpoint_tensor_allowed_q(), tuple(range(9)))
        self.assertLessEqual(check.tensor_diagonal_lower(8), 88)
        self.assertGreater(check.tensor_diagonal_lower(9), 88)

    def test_minimum_mod_four_diagonals(self) -> None:
        self.assertEqual(
            [check.minimum_diagonal_units(q) for q in range(9)],
            [3, 1, 1, 1, 3, 6, 10, 15, 21],
        )


class HarmonicTests(unittest.TestCase):
    def test_harmonic_projection_constants(self) -> None:
        self.assertEqual(
            check.harmonic_constants(2)["unscaled_trace_subtraction"],
            Fraction(24, 23),
        )
        self.assertEqual(check.harmonic_kernel(4), 1376)
        self.assertEqual(
            {m: check.harmonic_kernel(m) for m in (1, 0, -1, -2)},
            {1: -1, 0: 0, -1: 1, -2: -136},
        )
        for q in range(13):
            constants = check.harmonic_constants(q)
            self.assertEqual(constants["diagonal"], 1376)
            self.assertEqual(constants["row_sum"], 138 * (q - 2))
            self.assertEqual(constants["total_sum"], 1104)

    def test_harmonic_cauchy_endpoint(self) -> None:
        # q=10 passes the one-vector bound; q=11 fails it.
        self.assertGreaterEqual(check.centered_harmonic_diagonal(10), 0)
        self.assertLess(check.centered_harmonic_diagonal(11), 0)

    def test_centered_q10_minors(self) -> None:
        self.assertEqual(check.centered_harmonic_diagonal(10), 272)
        for q in range(0, 6):
            for m in (1, 0, -1, -2):
                self.assertGreaterEqual(check.centered_minor_determinant(10, q, m), 0)
        for q in range(6, 11):
            for m in (1, 0, -1, -2):
                self.assertLess(check.centered_minor_determinant(10, q, m), 0)


class TraceSquareTests(unittest.TestCase):
    def test_two_projector_factors_and_trace_cyclicity(self) -> None:
        # M^2=2M in this toy example.  The exact identity must contain two
        # factors of 2, not one.
        m = ((1, 1), (1, 1))
        w = ((2, 3), (3, 5))

        def multiply(left, right):
            return tuple(
                tuple(
                    sum(left[i][k] * right[k][j] for k in range(2))
                    for j in range(2)
                )
                for i in range(2)
            )

        def trace(matrix):
            return sum(matrix[i][i] for i in range(2))

        a = multiply(multiply(m, w), m)
        trace_a_squared = trace(multiply(a, a))
        t = trace(multiply(multiply(m, w), multiply(m, w)))
        self.assertEqual(trace_a_squared, 2**2 * t)
        self.assertNotEqual(trace_a_squared, 2 * t)

    def test_cyclic_factor(self) -> None:
        constants = check.trace_square_constants()
        self.assertEqual(constants["factor"], 441)
        self.assertEqual(constants["rank_trace_bound"], Fraction(576, 11))
        self.assertEqual(constants["raw_integer_bound"], 53)

    def test_ordered_unordered_parity(self) -> None:
        odd = check.odd_entry_counts_at_endpoint()
        self.assertEqual(odd, {"ordered": 6500, "unordered": 3250})
        constants = check.trace_square_constants()
        self.assertEqual(constants["trace_square_mod_8"], 4)
        self.assertEqual(constants["t_mod_8"], 4)
        # Hostile mutation: treating the ordered count as unordered changes
        # the residue and would incorrectly remove the strengthening.
        self.assertEqual((2 * odd["ordered"]) % 8, 0)

    def test_rank_trace_and_congruence_strengthening(self) -> None:
        constants = check.trace_square_constants()
        self.assertEqual(constants["t_minimum"], 60)
        self.assertEqual(constants["trace_square_minimum"], 26460)
        self.assertLess(441 * 53, 26460)
        self.assertEqual(60 % 8, 4)


class ScalarRelaxationTests(unittest.TestCase):
    def test_profile_count_keeps_q_one(self) -> None:
        self.assertEqual(check.count_scalar_profiles(True), 22113)
        self.assertEqual(check.count_scalar_profiles(False), 148)

    def test_survivor_is_only_aggregate(self) -> None:
        witness = check.scalar_survivor()
        self.assertEqual(witness["diagonal_sum"], 1008)
        self.assertEqual(witness["trace_square"], 26460)
        self.assertEqual(witness["off_diagonal_ordered_square_energy"], 21756)
        self.assertEqual(witness["additional_unordered_magnitude_two_pairs"], 1907)
        self.assertEqual(witness["scope"], "aggregate scalar relaxation only")

    def test_spectral_witness_is_only_a_moment_witness(self) -> None:
        witness = check.spectral_moment_witness()
        self.assertEqual(witness["rank"], 44)
        self.assertTrue(witness["smaller_value_positive"])
        self.assertEqual(witness["sum"], 1008)
        self.assertEqual(witness["sum_squares"], 26460)
        self.assertEqual(
            witness["scope"],
            "nonnegative spectral first-two-moment relaxation only",
        )

    def test_status_boundary(self) -> None:
        status = check.build_results()["status"]
        self.assertFalse(status["endpoint_excluded"])
        self.assertFalse(status["target_resolved"])
        self.assertFalse(status["novelty_assessed"])


if __name__ == "__main__":
    unittest.main()
