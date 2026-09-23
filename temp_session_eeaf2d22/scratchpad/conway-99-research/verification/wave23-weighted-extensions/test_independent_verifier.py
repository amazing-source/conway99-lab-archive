#!/usr/bin/env python3
"""Hostile tests for the independent Wave-23 weighted-extension verifier."""

from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

import independent_verifier as verifier


class IndependentWeightedExtensionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.repo = Path(__file__).resolve().parents[2]
        cls.witness = verifier.load_json(
            cls.repo / "attempts/wave23-weighted-extensions/affine-witness.json"
        )
        cls.source21 = verifier.load_json(
            cls.repo / "attempts/wave21-six-vertex-lp/exact-results.json"
        )
        cls.source22 = verifier.load_json(
            cls.repo / "attempts/wave22-full-seven-deck/exact-results.json"
        )
        cls.baseline = verifier.validate_candidate(
            cls.witness, cls.source21, cls.source22
        )

    def mutation(self) -> dict[str, object]:
        return copy.deepcopy(self.witness)

    def reject(self, payload: dict[str, object]) -> None:
        with self.assertRaises((AssertionError, KeyError, TypeError, ValueError)):
            verifier.validate_candidate(payload, self.source21, self.source22)

    def test_01_baseline_is_scoped_verified(self) -> None:
        self.assertEqual(self.baseline["claim_label"], "VERIFIED")
        self.assertIs(
            self.baseline["scope_wall"]["target_existence_status"] == "UNKNOWN",
            True,
        )

    def test_02_parameter_mutation_is_rejected(self) -> None:
        payload = self.mutation()
        payload["parameters"]["n3"] = 708
        self.reject(payload)

    def test_03_parameter_omission_is_rejected(self) -> None:
        payload = self.mutation()
        del payload["parameters"]["mu"]
        self.reject(payload)

    def test_04_lower_record_omission_is_rejected(self) -> None:
        payload = self.mutation()
        payload["independent_lower_counts"].pop()
        self.reject(payload)

    def test_05_lower_mask_reordering_is_rejected(self) -> None:
        payload = self.mutation()
        masks = payload["independent_lower_counts"][4]["canonical_masks"]
        masks[0], masks[1] = masks[1], masks[0]
        self.reject(payload)

    def test_06_lower_count_mutation_is_rejected(self) -> None:
        payload = self.mutation()
        payload["independent_lower_counts"][3]["counts"][2] += 1
        self.reject(payload)

    def test_07_boolean_count_is_rejected(self) -> None:
        payload = self.mutation()
        payload["independent_lower_counts"][2]["counts"][0] = True
        self.reject(payload)

    def test_08_seven_record_omission_is_rejected(self) -> None:
        payload = self.mutation()
        payload["order_seven_affine_family"]["records"].pop()
        self.reject(payload)

    def test_09_seven_record_reordering_is_rejected(self) -> None:
        payload = self.mutation()
        records = payload["order_seven_affine_family"]["records"]
        records[7], records[8] = records[8], records[7]
        self.reject(payload)

    def test_10_base_witness_mutation_is_rejected(self) -> None:
        payload = self.mutation()
        payload["order_seven_affine_family"]["records"][0]["count_at_z_min"] += 1
        self.reject(payload)

    def test_11_kernel_delta_mutation_is_rejected(self) -> None:
        payload = self.mutation()
        payload["order_seven_affine_family"]["records"][100]["delta_per_z"] -= 1
        self.reject(payload)

    def test_12_boolean_delta_is_rejected(self) -> None:
        payload = self.mutation()
        payload["order_seven_affine_family"]["records"][0]["delta_per_z"] = False
        self.reject(payload)

    def test_13_family_row_omission_disclosure_is_rejected(self) -> None:
        payload = self.mutation()
        payload["order_seven_affine_family"]["exact_rows_checked"] = 711
        self.reject(payload)

    def test_14_H_input_disclosure_mutation_is_rejected(self) -> None:
        payload = self.mutation()
        payload["hamiltonian_comparison"]["solver_inputs"].append("H_0")
        self.reject(payload)

    def test_15_H_noninput_omission_is_rejected(self) -> None:
        payload = self.mutation()
        payload["hamiltonian_comparison"]["not_solver_inputs"].pop()
        self.reject(payload)

    def test_16_H_record_mutation_is_rejected(self) -> None:
        payload = self.mutation()
        payload["hamiltonian_comparison"]["records"][3]["delta_per_z"] += 1
        self.reject(payload)

    def test_17_hidden_H_field_is_rejected(self) -> None:
        payload = self.mutation()
        payload["hamiltonian_comparison"]["extra_constraint"] = "H_0"
        self.reject(payload)

    def test_18_private_windows_path_is_rejected(self) -> None:
        payload = self.mutation()
        payload["warnings"].append("Z:" + "/private/data.txt")
        self.reject(payload)

    def test_19_private_posix_path_is_rejected(self) -> None:
        payload = self.mutation()
        payload["warnings"].append("/home/" + "someone/private.txt")
        self.reject(payload)

    def test_20_top_level_hidden_field_is_rejected(self) -> None:
        payload = self.mutation()
        payload["extra_assumption"] = "transitive"
        self.reject(payload)


if __name__ == "__main__":
    unittest.main()
