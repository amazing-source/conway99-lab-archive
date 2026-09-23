#!/usr/bin/env python3
"""Exact and hostile tests for the Wave151 clean-room verifier."""

from __future__ import annotations

import json
import unittest

import independent_verify as verifier


class Wave151IndependentVerifierTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = verifier.build_result()

    def test_frozen_inputs_and_separation(self) -> None:
        self.assertEqual(
            verifier.sha256_file(verifier.DISCOVERY_MANIFEST),
            verifier.EXPECTED_DISCOVERY_MANIFEST_SHA256,
        )
        self.assertEqual(
            verifier.sha256_file(verifier.DISCOVERY_RESULT),
            verifier.EXPECTED_DISCOVERY_RESULT_SHA256,
        )
        self.assertFalse(
            self.result["frozen_inputs"]["discovery_code_imported_or_executed"]
        )

    def test_edge_universe_is_k12_minus_matching(self) -> None:
        edges = verifier.nonmatching_edges()
        self.assertEqual(len(edges), 60)
        self.assertEqual(
            set(edges).intersection({(left, left + 1) for left in range(0, 12, 2)}),
            set(),
        )
        self.assertEqual(
            [list(edge) for edge in edges],
            self.result["factor_semantics"]["edge_columns"],
        )

    def test_q1_and_binary_factor_semantics(self) -> None:
        semantics = self.result["factor_semantics"]
        verifier.validate_permutation(semantics["Q1"], "Q1")
        factor = self.result["partial_factor"]
        self.assertEqual(factor["shape"], [24, 60])
        self.assertTrue(factor["all_entries_binary"])
        self.assertEqual(factor["row_sums"], [10] * 24)
        self.assertEqual(factor["group_zero_column_sums"], [2] * 60)
        self.assertEqual(factor["group_one_column_sums"], [2] * 60)
        self.assertEqual(factor["combined_column_sums"], [4] * 60)
        self.assertEqual(
            factor["binary_matrix_sha256"],
            "11dd68b64c237e6d45e221e8910b3da69e9492dd01aeb697555d874fdab9eed5",
        )

    def test_all_relevant_gram_blocks(self) -> None:
        blocks = self.result["gram_blocks"]
        self.assertEqual(blocks["total_entries_checked"], 576)
        self.assertEqual(
            blocks["G00"]["sha256"],
            "a3e4e131fb05463e586a880b9915523c286281f3c2e3622843b3a2353745b4f1",
        )
        self.assertEqual(blocks["G11"]["sha256"], blocks["G00"]["sha256"])
        self.assertEqual(
            blocks["G01"]["sha256"],
            "21330ee4f3ba598ae0535586a34c34d9e7a7a63552bb81eab6656a5ddfda5fc4",
        )
        self.assertEqual(blocks["G10"]["sha256"], blocks["G01"]["sha256"])
        self.assertTrue(all(blocks[name]["exact_match"] for name in ("G00", "G11", "G01", "G10")))

    def test_hostile_binary_bit_flip_is_rejected(self) -> None:
        binary = [row[:] for row in self.result["partial_factor"]["binary_rows"]]
        binary[0][0] ^= 1
        parent = json.loads(verifier.WAVE149_RESULT.read_text(encoding="utf-8"))
        gram = parent["minimal_surviving_witness"]["gram_rows"]
        target = verifier.block_matrix(
            verifier.target_block(gram, 0, 0),
            verifier.target_block(gram, 0, 12),
            verifier.target_block(gram, 12, 0),
            verifier.target_block(gram, 12, 12),
        )
        with self.assertRaises(AssertionError):
            verifier.validate_partial_factor(
                binary,
                target,
                self.result["partial_factor"]["binary_matrix_sha256"],
            )

    def test_hostile_q1_duplicate_is_rejected(self) -> None:
        hostile = list(self.result["factor_semantics"]["Q1"])
        hostile[0] = hostile[1]
        with self.assertRaisesRegex(AssertionError, "not a permutation"):
            verifier.validate_permutation(hostile, "hostile Q1")
        self.assertTrue(self.result["hostile_tests"]["Q1_duplicate_rejected"])
        self.assertTrue(self.result["hostile_tests"]["Q1_value_swap_rejected"])

    def test_retained_q2_residual_is_exact_but_not_a_certificate(self) -> None:
        residual = self.result["retained_Q2_residual"]
        self.assertEqual(residual["G02_squared_residual"], 40)
        self.assertEqual(residual["G12_squared_residual"], 40)
        self.assertEqual(residual["total_squared_residual"], 80)
        self.assertFalse(residual["is_exact_third_group"])
        self.assertFalse(residual["certificate_authority"])

    def test_unsat_is_only_a_solver_diagnostic(self) -> None:
        audit = self.result["fixed_Q1_solver_audit"]
        self.assertEqual(audit["independently_reconstructed_boolean_variables"], 1620)
        self.assertEqual(audit["domain_exact_one_constraints"], 60)
        self.assertEqual(audit["image_exact_one_constraints"], 60)
        self.assertEqual(audit["vertex_pair_capacity_constraints"], 288)
        self.assertFalse(audit["proof_artifact_present"])
        self.assertEqual(audit["verdict"], "UNVERIFIED_SOLVER_DIAGNOSTIC")
        self.assertEqual(audit["scope"], "extension of the one stored Q1 only")

    def test_unrestricted_residual_has_no_replayable_candidate(self) -> None:
        residual = self.result["unrestricted_joint_residual"]
        self.assertEqual(residual["stored_score"], 108)
        self.assertEqual(residual["replay_status"], "UNREPLAYABLE_SCORE_ONLY")
        self.assertFalse(residual["certificate_authority"])

    def test_full_problem_stays_unknown(self) -> None:
        verdict = self.result["verdict"]
        self.assertEqual(verdict["24x60_binary_factor"], "VERIFIED")
        self.assertEqual(verdict["36x60_C"], "UNKNOWN")
        self.assertEqual(verdict["60x60_D"], "UNKNOWN_NOT_REACHED")
        self.assertEqual(verdict["graph_realization"], "UNKNOWN")
        self.assertEqual(verdict["Conway_99"], "UNKNOWN")
        self.assertEqual(verdict["strict_n3_upper_bound"], "NOT_IMPROVED")

    def test_stored_result_replays_semantically(self) -> None:
        stored = json.loads(
            (verifier.HERE / "independent-results.json").read_text(encoding="utf-8")
        )
        current = dict(self.result)
        current.pop("resource_report")
        stored.pop("resource_report")
        self.assertEqual(current, stored)


if __name__ == "__main__":
    unittest.main()
