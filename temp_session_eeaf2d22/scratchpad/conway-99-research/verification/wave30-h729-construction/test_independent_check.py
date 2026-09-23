#!/usr/bin/env python3
"""Hostile tests for the blind Wave 30 h729 construction verifier."""

from __future__ import annotations

import copy
import itertools
import json
import math
import unittest
from fractions import Fraction

import independent_check as check


class IndependentConstructionVerifierTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.submission = json.loads(check.SUBMISSION_PATH.read_text(encoding="utf-8"))
        cls.final_gram = check.qmatrix(
            cls.submission["rank20_construction"]["T20"]["gram"], "T20 test input"
        )
        cls.steps = cls.submission["rank20_construction"]["neighbor_chain"]
        cls.chain = check.reconstruct_chain(cls.final_gram, cls.steps)
        cls.full_result = check.run_verification(cls.submission)

    def test_01_frozen_inputs_match(self) -> None:
        self.assertEqual(
            check.sha256_file(check.SUBMISSION_PATH), check.EXPECTED_SUBMISSION_SHA256
        )
        self.assertEqual(check.sha256_file(check.REPORT_PATH), check.EXPECTED_REPORT_SHA256)

    def test_02_full_result_is_scoped_verified_claim(self) -> None:
        self.assertEqual(self.full_result["claim_label"], "VERIFIED")
        scope = self.full_result["scope"]
        self.assertTrue(scope["bare_S_G_only"])
        self.assertEqual(scope["n3_708_status"], "UNKNOWN")
        self.assertEqual(scope["conway_99_graph_status"], "UNKNOWN")

    def test_03_decisive_counts_and_identity(self) -> None:
        self.assertEqual(
            self.full_result["rank20_chain"]["root_count_chain"],
            [240, 112, 48, 20, 6, 0],
        )
        self.assertEqual(
            self.full_result["rank20_chain"]["T20_shell_through_norm_4"]["counts"],
            {"0": 1, "4": 5076},
        )
        self.assertTrue(self.full_result["rank44"]["SG_equals_21I"])

    def test_04_enumerator_matches_independent_cartesian_box(self) -> None:
        gram = [
            [Fraction(4), Fraction(1), Fraction(0)],
            [Fraction(1), Fraction(4), Fraction(1)],
            [Fraction(0), Fraction(1), Fraction(4)],
        ]
        cap = 10
        gram_inverse = check.inverse(gram)
        bounds = []
        for index in range(3):
            squared = Fraction(cap) * gram_inverse[index][index]
            upper = math.isqrt(check.floor_fraction(squared))
            if Fraction(upper * upper) < squared:
                upper += 1
            bounds.append(upper)
        brute = {
            vector
            for vector in itertools.product(
                *[range(-bound, bound + 1) for bound in bounds]
            )
            if check.qform(gram, vector) <= cap
        }
        exact = check.enumerate_short_vectors(gram, cap)
        enumerated = {
            vector
            for vectors in exact["_vectors"].values()
            for vector in vectors
        }
        self.assertEqual(enumerated, brute)

    def test_05_enumerator_keeps_exact_boundary(self) -> None:
        gram = [[Fraction(2)]]
        at_two = check.enumerate_short_vectors(gram, 2)
        below_two = check.enumerate_short_vectors(gram, 1)
        self.assertEqual(at_two["counts"], {"0": 1, "2": 2})
        self.assertEqual(below_two["counts"], {"0": 1})

    def test_06_enumerator_is_unimodular_basis_invariant(self) -> None:
        gram = [
            [Fraction(4), Fraction(1), Fraction(0)],
            [Fraction(1), Fraction(4), Fraction(1)],
            [Fraction(0), Fraction(1), Fraction(4)],
        ]
        transform = [
            [Fraction(1), Fraction(1), Fraction(0)],
            [Fraction(0), Fraction(1), Fraction(-1)],
            [Fraction(0), Fraction(0), Fraction(1)],
        ]
        changed = check.changed_basis_gram(gram, transform)
        self.assertEqual(
            check.enumerate_short_vectors(gram, 12)["counts"],
            check.enumerate_short_vectors(changed, 12)["counts"],
        )

    def test_07_nonsymmetry_is_rejected(self) -> None:
        bad = [[Fraction(4), Fraction(1)], [Fraction(0), Fraction(4)]]
        with self.assertRaises(check.VerificationError):
            check.check_gram(bad, "nonsymmetric hostile input")

    def test_08_odd_lattice_is_rejected(self) -> None:
        bad = [[Fraction(3), Fraction(0)], [Fraction(0), Fraction(4)]]
        with self.assertRaises(check.VerificationError):
            check.check_gram(bad, "odd hostile input")

    def test_09_indefinite_lattice_is_rejected(self) -> None:
        bad = [[Fraction(2), Fraction(3)], [Fraction(3), Fraction(2)]]
        with self.assertRaises(check.VerificationError):
            check.check_gram(bad, "indefinite hostile input")

    def test_10_mutated_neighbor_basis_is_rejected(self) -> None:
        entry = copy.deepcopy(self.steps[0])
        entry["neighbor_basis_P"][0][0] += 1
        with self.assertRaises(check.VerificationError):
            check.verify_neighbor_step(self.chain[0], self.chain[1], entry)

    def test_11_transposed_neighbor_basis_is_rejected(self) -> None:
        entry = copy.deepcopy(self.steps[0])
        entry["neighbor_basis_P"] = [
            list(row) for row in zip(*entry["neighbor_basis_P"])
        ]
        with self.assertRaises(check.VerificationError):
            check.verify_neighbor_step(self.chain[0], self.chain[1], entry)

    def test_12_nonunimodular_reduction_is_rejected(self) -> None:
        entry = copy.deepcopy(self.steps[0])
        entry["exact_lll_row_transform_U"][0] = [
            2 * value for value in entry["exact_lll_row_transform_U"][0]
        ]
        with self.assertRaises(check.VerificationError):
            check.verify_neighbor_step(self.chain[0], self.chain[1], entry)

    def test_13_deleted_support_is_rejected(self) -> None:
        entry = copy.deepcopy(self.steps[0])
        entry["support_in_previous_reduced_basis"] = []
        with self.assertRaises(check.VerificationError):
            check.verify_neighbor_step(self.chain[0], self.chain[1], entry)

    def test_14_wrong_support_is_rejected(self) -> None:
        entry = copy.deepcopy(self.steps[0])
        entry["support_in_previous_reduced_basis"] = [0]
        with self.assertRaises(check.VerificationError):
            check.verify_neighbor_step(self.chain[0], self.chain[1], entry)

    def test_15_wrong_parity_pivot_is_rejected(self) -> None:
        entry = copy.deepcopy(self.steps[0])
        pairing = check.matvec(
            self.chain[0],
            [
                Fraction(
                    1 if index in entry["support_in_previous_reduced_basis"] else 0
                )
                for index in range(20)
            ],
        )
        even_index = next(
            index for index, value in enumerate(pairing) if value.numerator % 2 == 0
        )
        entry["parity_pivot"] = even_index
        with self.assertRaises(check.VerificationError):
            check.verify_neighbor_step(self.chain[0], self.chain[1], entry)

    def test_16_wrong_submitted_inverse_is_rejected(self) -> None:
        entry = copy.deepcopy(self.steps[0])
        entry["neighbor_basis_P_inverse"][0][0] = 0
        with self.assertRaises(check.VerificationError):
            check.verify_neighbor_step(self.chain[0], self.chain[1], entry)

    def test_17_mutated_following_gram_is_rejected(self) -> None:
        bad_following = copy.deepcopy(self.chain[1])
        bad_following[0][0] += 2
        with self.assertRaises(check.VerificationError):
            check.verify_neighbor_step(self.chain[0], bad_following, self.steps[0])

    def test_18_all_neighbor_common_indices_are_two(self) -> None:
        for index, entry in enumerate(self.steps):
            report = check.verify_neighbor_step(
                self.chain[index], self.chain[index + 1], entry
            )
            self.assertEqual(report["index_previous_over_common"], 2)
            self.assertEqual(report["index_neighbor_over_common"], 2)

    def test_19_cross_block_coupling_is_rejected(self) -> None:
        candidate_s = check.qmatrix(self.submission["rank44_candidate"]["S"], "S")
        candidate_s[0][20] = Fraction(1)
        candidate_s[20][0] = Fraction(1)
        with self.assertRaises(check.VerificationError):
            check.extract_direct_sum_leech(candidate_s, self.final_gram)

    def test_20_wrong_scaled_dual_is_rejected(self) -> None:
        submitted = check.qmatrix(
            self.submission["rank20_construction"]["T20"][
                "scaled_dual_21_T20_inverse"
            ],
            "scaled dual",
        )
        submitted[0][0] += 2
        with self.assertRaises(check.VerificationError):
            check.verify_dual(self.final_gram, 21, submitted)

    def test_21_missing_nonconstruction_disclaimer_is_rejected(self) -> None:
        hostile = copy.deepcopy(self.submission)
        hostile["rank44_candidate"]["not_constructed"] = ["a graph"]
        with self.assertRaises(check.VerificationError):
            check.verify_scope(hostile)

    def test_22_global_resolution_inflation_is_rejected(self) -> None:
        hostile = copy.deepcopy(self.submission)
        hostile["restrictions"]["global_status"] = "Conway-99 is resolved."
        with self.assertRaises(check.VerificationError):
            check.verify_scope(hostile)

    def test_23_fraction_parser_rejects_zero_denominator(self) -> None:
        with self.assertRaises(check.VerificationError):
            check.parse_fraction("1/0")

    def test_24_bareiss_matches_fraction_determinant(self) -> None:
        integer = [[4, 1, 0], [1, 4, 1], [0, 1, 4]]
        fraction = [[Fraction(value) for value in row] for row in integer]
        self.assertEqual(check.det_bareiss(integer), check.det_fraction(fraction))


if __name__ == "__main__":
    unittest.main(verbosity=2)
