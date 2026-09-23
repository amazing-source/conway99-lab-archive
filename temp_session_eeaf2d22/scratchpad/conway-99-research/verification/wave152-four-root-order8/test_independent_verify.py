#!/usr/bin/env python3
"""Exact and hostile regression tests for the Wave152 clean-room verifier."""

from __future__ import annotations

import math
import unittest

import independent_verify as verifier


class Wave152IndependentVerifierTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = verifier.build_result()
        cls.by_root = {
            block["root_mask"]: block for block in cls.result["root_blocks"]
        }

    def test_discovery_inputs_remain_hash_frozen(self) -> None:
        self.assertEqual(
            verifier.sha256_file(verifier.DISCOVERY_CODE),
            verifier.EXPECTED_DISCOVERY_CODE_SHA256,
        )
        self.assertEqual(
            verifier.sha256_file(verifier.DISCOVERY_RESULT),
            verifier.EXPECTED_DISCOVERY_RESULT_SHA256,
        )
        self.assertFalse(
            self.result["inputs"]["discovery_code_imported_or_executed"]
        )

    def test_nine_pointwise_root_flag_universes(self) -> None:
        self.assertEqual(
            tuple(self.result["semantics"]["root_masks"]),
            verifier.ROOT_MASKS,
        )
        self.assertEqual(
            [self.by_root[mask]["flag_count"] for mask in verifier.ROOT_MASKS],
            [224, 201, 155, 99, 69, 178, 125, 60, 70],
        )
        for root_mask, block in self.by_root.items():
            verifier.verify_flag_semantics(root_mask, block["flag_masks"])

    def test_union_order_enumeration(self) -> None:
        self.assertEqual(
            self.result["enumeration"],
            {
                "6": {
                    "nonzero_classes": 61,
                    "matched_root_embeddings_unweighted": 5028,
                    "emitted_products_unweighted": 5028,
                },
                "7": {
                    "nonzero_classes": 204,
                    "matched_root_embeddings_unweighted": 38576,
                    "emitted_products_unweighted": 231456,
                },
                "8": {
                    "nonzero_classes": 874,
                    "matched_root_embeddings_unweighted": 333278,
                    "emitted_products_unweighted": 1999668,
                },
            },
        )

    def test_lower_counts_are_deletion_derived(self) -> None:
        reconstruction = self.result["count_reconstruction"]
        self.assertEqual(
            reconstruction["support_sizes"],
            {"x4": 9, "x5": 21, "x6": 61, "x7": 204, "x8": 874},
        )
        self.assertEqual(
            reconstruction["x6_sha256"],
            "f6c8adc240488d97b77bd92d136d0d79ecff0ddb7f6db693352563829d53b40a",
        )
        self.assertIn("deletion identities", reconstruction["route"])

    def test_integer_scaling_and_totals(self) -> None:
        free_pairs = math.comb(95, 2)
        for block in self.result["root_blocks"]:
            root_count = block["root_embedding_count"]
            self.assertEqual(block["first_moment_total"], root_count * free_pairs)
            self.assertEqual(
                block["second_moment_total"],
                root_count * free_pairs * free_pairs,
            )
            self.assertEqual(block["centered_scale"], "4*(R*M-s*s^T)")

    def test_mask_3_negative_certificate(self) -> None:
        certificate = self.by_root[3]["negative_certificate"]
        self.assertEqual(certificate["support_size"], 24)
        self.assertEqual(
            certificate["quadratic_value_scaled"],
            "-2293145527521819747490560",
        )
        self.assertTrue(certificate["proves_centered_block_not_psd"])
        self.assertEqual(self.by_root[3]["exact_status"], "NOT_PSD")

    def test_mask_12_negative_certificate(self) -> None:
        certificate = self.by_root[12]["negative_certificate"]
        self.assertEqual(certificate["support_size"], 88)
        self.assertEqual(
            certificate["quadratic_value_scaled"],
            "-8605517548253993047296",
        )
        self.assertTrue(certificate["proves_centered_block_not_psd"])
        self.assertEqual(self.by_root[12]["exact_status"], "NOT_PSD")

    def test_hostile_vector_mutations_are_rejected(self) -> None:
        for root_mask in (3, 12):
            certificate = self.by_root[root_mask]["negative_certificate"]
            self.assertTrue(certificate["hostile_mutation_rejected"])
            self.assertNotEqual(
                certificate["hostile_first_coordinate_plus_one_value_scaled"],
                certificate["quadratic_value_scaled"],
            )

    def test_hostile_flag_semantics_mutation_is_rejected(self) -> None:
        block = self.by_root[3]
        certificate = block["negative_certificate"]
        hostile_flags = list(certificate["flag_masks"])
        hostile_flags[0] = block["flag_masks"][certificate["indices"][0] + 1]
        with self.assertRaisesRegex(
            AssertionError, "certificate index/flag semantics"
        ):
            verifier.verify_certificate_flag_semantics(
                block["flag_masks"],
                certificate["indices"],
                hostile_flags,
            )

    def test_zero_blocks_and_unresolved_blocks_are_not_conflated(self) -> None:
        self.assertEqual(self.by_root[15]["exact_status"], "EXACTLY_PSD_ZERO")
        self.assertEqual(self.by_root[30]["exact_status"], "EXACTLY_PSD_ZERO")
        for root_mask in (0, 1, 7, 11, 13):
            self.assertEqual(
                self.by_root[root_mask]["exact_status"],
                "UNKNOWN_NO_NEGATIVE_CERTIFICATE",
            )

    def test_verdict_is_only_about_the_pseudowitness(self) -> None:
        verdict = self.result["verdict"]
        self.assertEqual(verdict["wave150_pseudowitness"], "REFUTED")
        self.assertEqual(verdict["endpoint_n3_4158"], "UNKNOWN")
        self.assertEqual(verdict["Conway_99"], "UNKNOWN")
        self.assertEqual(verdict["strict_upper_bound"], "NOT_PROVED")


if __name__ == "__main__":
    unittest.main()
