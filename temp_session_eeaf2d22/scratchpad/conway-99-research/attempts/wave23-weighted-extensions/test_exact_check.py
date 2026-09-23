#!/usr/bin/env python3
"""Hostile tests for the Wave-23 exact affine checker."""

from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

import exact_check
import model


class ExactAffineCheckerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.path = Path(__file__).with_name("affine-witness.json")
        cls.payload = json.loads(cls.path.read_text(encoding="utf-8"))
        cls.baseline = exact_check.validate_witness(cls.payload)

    def mutated(self) -> dict[str, object]:
        return copy.deepcopy(self.payload)

    def assert_rejected(self, payload: dict[str, object]) -> None:
        with self.assertRaises((AssertionError, KeyError, TypeError, ValueError)):
            exact_check.validate_witness(payload)

    def test_01_baseline_passes(self) -> None:
        self.assertEqual(
            self.baseline["conclusion"]["full_allowed_interval"],
            "EXACTLY_FEASIBLE",
        )

    def test_02_affine_helper_uses_admissible_points(self) -> None:
        affine = model.hamiltonian_affine_counts(model.N3)
        self.assertEqual(len(affine), 19)
        self.assertEqual(affine[11], (0, 4))

    def test_03_schema_mutation_rejected(self) -> None:
        payload = self.mutated()
        payload["schema_version"] = 2
        self.assert_rejected(payload)

    def test_04_parameter_mutation_rejected(self) -> None:
        payload = self.mutated()
        payload["parameters"]["n3"] = 708
        self.assert_rejected(payload)

    def test_05_lower_chain_truncation_rejected(self) -> None:
        payload = self.mutated()
        payload["independent_lower_counts"].pop()
        self.assert_rejected(payload)

    def test_06_lower_mask_reordering_rejected(self) -> None:
        payload = self.mutated()
        masks = payload["independent_lower_counts"][4]["canonical_masks"]
        masks[0], masks[1] = masks[1], masks[0]
        self.assert_rejected(payload)

    def test_07_lower_count_mutation_rejected(self) -> None:
        payload = self.mutated()
        payload["independent_lower_counts"][4]["counts"][0] += 1
        self.assert_rejected(payload)

    def test_08_boolean_count_rejected(self) -> None:
        payload = self.mutated()
        payload["independent_lower_counts"][2]["counts"][0] = True
        self.assert_rejected(payload)

    def test_09_missing_seven_class_rejected(self) -> None:
        payload = self.mutated()
        payload["order_seven_affine_family"]["records"].pop()
        self.assert_rejected(payload)

    def test_10_seven_mask_mutation_rejected(self) -> None:
        payload = self.mutated()
        payload["order_seven_affine_family"]["records"][20][
            "canonical_mask"
        ] += 1
        self.assert_rejected(payload)

    def test_11_base_count_mutation_rejected(self) -> None:
        payload = self.mutated()
        payload["order_seven_affine_family"]["records"][0][
            "count_at_z_min"
        ] += 1
        self.assert_rejected(payload)

    def test_12_delta_mutation_rejected(self) -> None:
        payload = self.mutated()
        payload["order_seven_affine_family"]["records"][100][
            "delta_per_z"
        ] -= 1
        self.assert_rejected(payload)

    def test_13_boolean_affine_value_rejected(self) -> None:
        payload = self.mutated()
        payload["order_seven_affine_family"]["records"][0][
            "delta_per_z"
        ] = False
        self.assert_rejected(payload)

    def test_14_hamiltonian_comparison_mutation_rejected(self) -> None:
        payload = self.mutated()
        payload["hamiltonian_comparison"]["records"][0][
            "delta_per_z"
        ] += 1
        self.assert_rejected(payload)

    def test_15_hamiltonian_input_disclosure_rejected(self) -> None:
        payload = self.mutated()
        payload["hamiltonian_comparison"]["solver_inputs"].append("H_0")
        self.assert_rejected(payload)

    def test_16_reordered_seven_records_rejected(self) -> None:
        payload = self.mutated()
        records = payload["order_seven_affine_family"]["records"]
        records[1], records[2] = records[2], records[1]
        self.assert_rejected(payload)

    def test_17_private_absolute_path_rejected(self) -> None:
        payload = self.mutated()
        payload["warnings"].append("Z:" + "/private.txt")
        self.assert_rejected(payload)

    def test_18_result_path_is_repo_relative(self) -> None:
        result = exact_check.validate_witness(
            self.payload,
            self.path.resolve(),
        )
        path = result["witness"]["path"]
        self.assertEqual(
            path,
            "attempts/wave23-weighted-extensions/affine-witness.json",
        )
        self.assertNotRegex(path, r"^[A-Za-z]:[\\/]")


if __name__ == "__main__":
    unittest.main()
