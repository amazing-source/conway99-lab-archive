#!/usr/bin/env python3
"""Hostile and regression tests for the Wave 20 exact checker."""

from __future__ import annotations

import copy
import unittest
from fractions import Fraction as F

import exact_check as check


class ExactIdentityTests(unittest.TestCase):
    def test_full_audit(self) -> None:
        result = check.audit()
        self.assertEqual(result["schur_bound"], 693)
        self.assertEqual(result["final_bound"]["n3_lower_bound"], 705)
        self.assertEqual(result["final_bound"]["induced_C6_lower_bound"], 209991)

    def test_incidence_spectra(self) -> None:
        check.validate_gamma_spectrum()
        self.assertEqual(check.C_EIGENVALUES, {18: 216, 7: -4, 0: -18, -3: 6})

    def test_projector_entries(self) -> None:
        coefficients = check.projector_coefficients(0)
        self.assertEqual(coefficients, (F(1, 7), F(1, 21), F(-1, 21), F(-1, 21)))
        self.assertEqual(
            check.projector_entry_data(coefficients),
            (F(4, 21), F(0), F(1, 21), F(-1, 21)),
        )

    def test_all_row_profiles(self) -> None:
        for q in range(13):
            profile = check.row_profile(q)
            self.assertEqual(sum(profile.values()), 212)
            self.assertEqual(sum(r * profile[r] for r in range(4)), 216)
            self.assertEqual(
                sum((r * (r - 1) // 2) * profile[r] for r in range(4)),
                36,
            )

    def test_cubic_endpoint(self) -> None:
        self.assertEqual(check.schur_triple(0, 0, 0), (F(-44, 147), F(4, 9261)))
        self.assertEqual(check.unscaled_cubic(), (F(-2772), F(4)))

    def test_equality_row_sum(self) -> None:
        profile = check.row_profile(2)
        row_cube = 4**3 + profile[0] - profile[2] - 8 * profile[3]
        self.assertEqual(row_cube, 0)
        self.assertEqual(profile, {0: 22, 1: 174, 2: 6, 3: 10})

    def test_integral_trace_threshold(self) -> None:
        bound = check.derive_final_bound()
        self.assertEqual(bound["trace_lower"], 924)
        self.assertEqual(bound["delta_threshold"], "11")
        self.assertEqual(bound["delta_multiple_of_three"], 12)

    def test_alternating_quadratic_lemma(self) -> None:
        check.validate_alternating_quadratic_lemma()
        matrix = [[0, 1], [1, 0]]
        for vector in ([0, 0], [1, 0], [0, 1], [1, 1]):
            self.assertEqual(check.quadratic_mod2(matrix, vector), 0)

    def test_nonzero_diagonal_mutation_breaks_alternating_lemma(self) -> None:
        mutated = [[1, 0], [0, 0]]
        self.assertEqual(check.quadratic_mod2(mutated, [1, 0]), 1)

    def test_gegenbauer_route_adds_nothing(self) -> None:
        result = check.gegenbauer_bounds(60)
        self.assertEqual(
            result["strongest_nonnegative_lower"],
            {"degree": 3, "bound": "693"},
        )
        self.assertGreater(F(result["strongest_nonnegative_upper"]["bound"]), 4158)


class HostileMutationTests(unittest.TestCase):
    def test_zero_eigenspace_multiplicity_mutation_rejected(self) -> None:
        mutated = dict(check.GAMMA_MULTIPLICITIES)
        mutated[0] = 43
        with self.assertRaises(check.InvariantError):
            check.validate_gamma_spectrum(mutated)

    def test_projector_sign_mutation_rejected(self) -> None:
        mutated = list(check.projector_coefficients(0))
        mutated[3] *= -1
        with self.assertRaises(check.InvariantError):
            check.validate_projector(0, mutated)

    def test_c_spectrum_mutation_rejected(self) -> None:
        mutated = dict(check.C_EIGENVALUES)
        mutated[0] = 18
        with self.assertRaises(check.InvariantError):
            check.validate_projector(0, check.projector_coefficients(0), mutated)

    def test_n3_ordered_pair_factor_mutation_detected(self) -> None:
        valid = check.unscaled_cubic()
        mutated = check.unscaled_cubic(check.global_ordered_counts(pair_factor=1))
        self.assertEqual(valid, (F(-2772), F(4)))
        self.assertNotEqual(mutated, valid)

    def test_missing_triangle_index_rejected_by_endpoint(self) -> None:
        valid = check.derive_final_bound()
        mutated = check.derive_final_bound(triangle_count=230)
        self.assertEqual(valid["trace_lower"], 924)
        self.assertEqual(mutated["trace_lower"], 920)
        self.assertNotEqual(valid, mutated)

    def test_removed_mod_four_premise_rejected(self) -> None:
        with self.assertRaises(check.InvariantError):
            check.derive_final_bound(diagonal_multiple_of_four=False)

    def test_removed_nonzero_row_premise_rejected(self) -> None:
        with self.assertRaises(check.InvariantError):
            check.derive_final_bound(every_mod2_row_nonzero=False)

    def test_delta_nine_cannot_pass_trace(self) -> None:
        self.assertLess(84 * 9, 4 * 231)


if __name__ == "__main__":
    unittest.main(verbosity=2)
