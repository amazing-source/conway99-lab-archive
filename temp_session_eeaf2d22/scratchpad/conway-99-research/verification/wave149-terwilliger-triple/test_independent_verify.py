#!/usr/bin/env python3
"""Regression and hostile-mutation tests for the clean-room Wave149 verifier."""

from __future__ import annotations

import hashlib
import json
import unittest

import independent_verify as verifier


class IndependentVerifierTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = verifier.build_result()

    def test_partition_is_forced_by_srg_parameters(self) -> None:
        partition = self.result["partition"]
        self.assertEqual(partition["fibres"], [12, 12, 12])
        self.assertEqual(partition["residual"], 60)
        self.assertEqual(partition["Ai_internal_degree"], 1)
        self.assertEqual(partition["Ai_to_each_other_Aj"], 1)
        self.assertEqual(partition["Ai_to_B"], 10)
        self.assertEqual(partition["B_to_each_Ai"], 2)
        self.assertEqual(partition["B_internal_degree"], 8)
        self.assertEqual(partition["incidence_balance_per_fibre"], 120)

    def test_matching_witness_is_prism_free(self) -> None:
        witness = self.result["matching_witness"]
        self.assertTrue(witness["commuting_involutions"])
        self.assertEqual(witness["composition"], witness["P"])
        self.assertEqual(witness["rooted_prism_fixed_points"], 0)

    def test_composition_matches_noncommuting_matrix_product(self) -> None:
        first = (1, 2, 0)
        second = (1, 0, 2)
        product = verifier.multiply(
            verifier.permutation_matrix(first),
            verifier.permutation_matrix(second),
        )
        self.assertEqual(
            product,
            verifier.permutation_matrix(verifier.compose(first, second)),
        )

    def test_gram_exact_invariants(self) -> None:
        gram = self.result["gram"]
        replayed_hash = hashlib.sha256(
            verifier.canonical_bytes(gram["rows"])
        ).hexdigest()
        self.assertEqual(gram["order"], 36)
        self.assertEqual(gram["sha256"], replayed_hash)
        self.assertEqual(gram["diagonal"], 10)
        self.assertEqual(gram["row_sum"], 60)
        self.assertEqual(gram["off_diagonal_minimum"], 0)
        self.assertEqual(gram["off_diagonal_maximum"], 2)
        self.assertEqual(gram["exact_rational_rank"], 32)
        self.assertTrue(gram["rank_condition_passes"])

    def test_exact_character_spectrum(self) -> None:
        certificate = self.result["psd_character_certificate"]
        self.assertEqual(
            certificate["exact_spectrum"],
            {"0": 4, "6": 9, "10": 9, "12": 13, "60": 1},
        )
        self.assertTrue(certificate["all_eigenvalues_nonnegative"])
        self.assertEqual(certificate["rank_from_characters"], 32)

    def test_hostile_gram_mutation_changes_certificate(self) -> None:
        rows = [row[:] for row in self.result["gram"]["rows"]]
        rows[0][1] += 1
        hostile_hash = hashlib.sha256(verifier.canonical_bytes(rows)).hexdigest()
        self.assertNotEqual(hostile_hash, self.result["gram"]["sha256"])
        self.assertNotEqual(rows, verifier.transpose(rows))

    def test_hostile_permutation_mutation_is_rejected(self) -> None:
        hostile = list(range(12))
        hostile[-1] = hostile[-2]
        with self.assertRaisesRegex(AssertionError, "not a permutation"):
            verifier.permutation_matrix(hostile)

    def test_stored_result_replays_exactly(self) -> None:
        stored = json.loads(
            (verifier.HERE / "independent-results.json").read_text(encoding="utf-8")
        )
        self.assertEqual(self.result, stored)

    def test_verdict_stays_scoped(self) -> None:
        verdict = self.result["verdict"]
        self.assertEqual(verdict["projection_feasible"], "VERIFIED_SCOPED")
        self.assertFalse(verdict["forces_a_prism"])
        self.assertEqual(verdict["binary_incidence_factor"], "UNKNOWN")
        self.assertFalse(verdict["graph_realization"])
        self.assertEqual(verdict["strict_n3_upper_bound"], "NOT_IMPROVED")
        self.assertEqual(verdict["Conway_99"], "UNKNOWN")


if __name__ == "__main__":
    unittest.main()
