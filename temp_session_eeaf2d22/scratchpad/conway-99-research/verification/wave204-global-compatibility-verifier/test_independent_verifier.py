#!/usr/bin/env python3
"""Acceptance and hostile mutation tests for the blind Wave204 verifier."""

from __future__ import annotations

import copy
import unittest

import independent_verifier as verifier


class ExactArithmeticTests(unittest.TestCase):
    def test_matrix_inverse(self) -> None:
        matrix = [[1, 2, 0], [0, 1, 1], [2, 0, 1]]
        inverse = verifier.matrix_inverse(matrix)
        self.assertEqual(verifier.mat_mul(matrix, inverse), verifier.identity(3))

    def test_source_blind_suite_passes(self) -> None:
        result = verifier.run_all()
        self.assertEqual(result["v1"]["claim_label"], "VERIFIED_SCOPED_RELAXED")
        self.assertEqual(result["v2"]["coboundary_claim_label"], "VERIFIED")
        self.assertEqual(result["v3"]["local_detector_claim_label"], "VERIFIED")


class V1MutationTests(unittest.TestCase):
    def assert_rejected(self, model: dict) -> None:
        with self.assertRaises(AssertionError):
            verifier.verify_v1(model)

    def test_deleted_degree_edge_rejected(self) -> None:
        model = verifier.build_v1_model()
        model["degree_edges"].pop()
        self.assert_rejected(model)

    def test_repeated_leaf_value_rejected(self) -> None:
        model = verifier.build_v1_model()
        model["pair_fibers"]["0"][1]["leaf_value"] = 0
        self.assert_rejected(model)

    def test_triple_core_mutation_rejected(self) -> None:
        model = verifier.build_v1_model()
        model["triple_families"]["0"] = [
            [0, 1, 2],
            [0, 1, 3],
            [0, 1, 4],
            [0, 1, 5],
            [0, 1, 6],
            [0, 2, 3],
            [0, 2, 4],
            [0, 2, 5],
            [0, 2, 6],
            [0, 3, 4],
            [0, 3, 5],
            [0, 3, 6],
            [0, 4, 5],
        ]
        self.assert_rejected(model)

    def test_slot_collision_rejected(self) -> None:
        model = verifier.build_v1_model()
        model["slot_rows"][1]["positions"][0] = model["slot_rows"][0]["positions"][0]
        self.assert_rejected(model)

    def test_false_full_occupancy_count_rejected(self) -> None:
        model = verifier.build_v1_model()
        model["nonprivate_labels"][0]["orientation_b"] = [2, 3, 4]
        self.assert_rejected(model)


class V2MutationTests(unittest.TestCase):
    def test_matched_projected_cycle_rejected(self) -> None:
        model = verifier.build_v2_model()
        model["cycles"][0]["next_outgoing_third_block_slot"] = 0
        with self.assertRaises(AssertionError):
            verifier.verify_v2(model)

    def test_invalid_s5_extension_rejected(self) -> None:
        model = verifier.build_v2_model()
        model["extensions"]["transposition_1_2"] = [0, 2, 2, 3, 4]
        with self.assertRaises(AssertionError):
            verifier.verify_v2(model)


class V3MutationTests(unittest.TestCase):
    def test_changed_cycle_expectation_rejected(self) -> None:
        wrong = {(6,): 0, (4, 2): 0, (3, 3): 0, (2, 2, 2): 0}
        with self.assertRaises(AssertionError):
            verifier.verify_v3(expected_h=wrong)

    def test_singular_witness_rejected(self) -> None:
        singular = copy.deepcopy(verifier.Y_WITNESS_1)
        for row in singular:
            row[5] = row[4]
        with self.assertRaises(AssertionError):
            verifier.verify_v3(witnesses=(singular, verifier.Y_WITNESS_2))


if __name__ == "__main__":
    unittest.main(verbosity=2)

