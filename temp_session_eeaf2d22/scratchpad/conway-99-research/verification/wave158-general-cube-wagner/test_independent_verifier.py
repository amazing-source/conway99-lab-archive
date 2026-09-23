"""Hostile mutation tests for the Wave158 clean-room verifier."""

from __future__ import annotations

import copy
import sys
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import independent_verifier as verifier  # noqa: E402


class Wave158HostileTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.certificate = verifier.build_certificate(check_memory=True)
        cls.payload = verifier.read_json(verifier.DISCOVERY_RESULTS_PATH)
        cls.stored_cut = verifier.read_json(verifier.STORED_CUT_PATH)
        verifier.verify_discovery_payload(
            cls.payload, cls.certificate, cls.stored_cut
        )

    def assert_payload_rejected(self, payload: dict) -> None:
        with self.assertRaises(verifier.VerificationError):
            verifier.verify_discovery_payload(
                payload, self.certificate, self.stored_cut
            )

    def test_live_manifests_pass(self) -> None:
        self.assertEqual(verifier.verify_manifest(verifier.MANIFEST_PATH), 8)
        self.assertEqual(verifier.verify_manifest(verifier.INPUT_FREEZE_PATH), 2)

    def test_root_mask_mutation_rejected(self) -> None:
        payload = copy.deepcopy(self.payload)
        payload["parameters"]["root_mask"] ^= 1
        self.assert_payload_rejected(payload)

    def test_plus_flag_mask_mutation_rejected(self) -> None:
        payload = copy.deepcopy(self.payload)
        payload["parameters"]["plus_flag_mask"] += 1
        self.assert_payload_rejected(payload)

    def test_cube_coefficient_mutation_rejected(self) -> None:
        payload = copy.deepcopy(self.payload)
        payload["quadratic_coefficients_before_division"]["8"]["2022000"] += 1
        self.assert_payload_rejected(payload)

    def test_wagner_mask_mutation_rejected(self) -> None:
        payload = copy.deepcopy(self.payload)
        payload["named_order8_masks"]["wagner_mobius_ladder"] += 1
        self.assert_payload_rejected(payload)

    def test_root_embedding_count_mutation_rejected(self) -> None:
        payload = copy.deepcopy(self.payload)
        payload["root_embedding_derivation"]["root_embedding_count"] += 1
        self.assert_payload_rejected(payload)

    def test_six_set_formula_mutation_rejected(self) -> None:
        payload = copy.deepcopy(self.payload)
        payload["six_set_formula"]["n3_coefficient"] = 0
        self.assert_payload_rejected(payload)

    def test_endpoint_gcd_mutation_rejected(self) -> None:
        payload = copy.deepcopy(self.payload)
        payload["endpoint_specialization"]["extra_endpoint_gcd"] = 1
        self.assert_payload_rejected(payload)

    def test_strict_bound_status_inflation_rejected(self) -> None:
        payload = copy.deepcopy(self.payload)
        payload["conclusion"]["strict_upper_bound_below_4158"] = "PROVED"
        self.assert_payload_rejected(payload)

    def test_named_isomorphisms_are_explicit(self) -> None:
        for record in self.certificate["named_graphs"].values():
            self.assertEqual(
                verifier.transform_mask(
                    record["labelled_mask"], 8, record["canonical_isomorphism"]
                ),
                record["canonical_mask"],
            )


if __name__ == "__main__":
    unittest.main()
