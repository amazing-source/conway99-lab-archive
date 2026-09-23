#!/usr/bin/env python3
"""Hostile tests for the exact full-seven-deck verifier."""

from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

import exact_check


HERE = Path(__file__).resolve().parent


class FullSevenDeckTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.model = exact_check.build_model()
        cls.payload = json.loads((HERE / "witness.json").read_text(encoding="utf-8"))

    def assert_rejected(self, payload: dict) -> None:
        with self.assertRaises((AssertionError, KeyError, TypeError, ValueError)):
            exact_check.validate_witness(payload, self.model)

    def test_frozen_witness_passes(self) -> None:
        result = exact_check.validate_witness(self.payload, self.model)
        self.assertEqual(result["deck_rows_passed"], 62)
        self.assertEqual(result["hamiltonian_types_passed"], 19)
        self.assertEqual(result["total_count"], 14_887_031_544)

    def test_independent_census_sizes(self) -> None:
        self.assertEqual(len(exact_check.admissible_labeled_masks(7)), 394_020)
        self.assertEqual(len(self.model["classes7"]), 208)
        self.assertEqual(len(self.model["classes6"]), 62)

    def test_finite_field_rank_profile(self) -> None:
        self.assertEqual(
            self.model["ranks"],
            {"2": 48, "3": 57, "5": 61, "7": 61, "11": 62},
        )

    def test_hamiltonian_transcription_is_complete(self) -> None:
        self.assertEqual(len(set(self.model["h_masks"])), 19)
        self.assertEqual(
            set(self.model["h_masks"]),
            set(exact_check.independently_enumerated_hamiltonian_classes()),
        )

    def test_every_deck_has_seven_cards(self) -> None:
        self.assertTrue(
            all(sum(column) == 7 for column in self.model["matrix_columns"])
        )

    def test_negative_count_is_rejected(self) -> None:
        payload = copy.deepcopy(self.payload)
        payload["classes"][0]["count"] = -1
        self.assert_rejected(payload)

    def test_boolean_count_is_rejected(self) -> None:
        payload = copy.deepcopy(self.payload)
        payload["classes"][0]["count"] = True
        self.assert_rejected(payload)

    def test_missing_class_is_rejected(self) -> None:
        payload = copy.deepcopy(self.payload)
        payload["classes"].pop()
        self.assert_rejected(payload)

    def test_reordered_classes_are_rejected(self) -> None:
        payload = copy.deepcopy(self.payload)
        payload["classes"][0], payload["classes"][1] = (
            payload["classes"][1],
            payload["classes"][0],
        )
        self.assert_rejected(payload)

    def test_unknown_mask_is_rejected(self) -> None:
        payload = copy.deepcopy(self.payload)
        payload["classes"][0]["canonical_mask"] ^= 1
        self.assert_rejected(payload)

    def test_deck_equation_mutation_is_rejected(self) -> None:
        payload = copy.deepcopy(self.payload)
        non_hamiltonian = next(
            record
            for record in payload["classes"]
            if record["canonical_mask"] not in set(self.model["h_masks"])
        )
        non_hamiltonian["count"] += 1
        self.assert_rejected(payload)

    def test_hamiltonian_count_mutation_is_rejected(self) -> None:
        payload = copy.deepcopy(self.payload)
        h0 = self.model["h_masks"][0]
        record = next(
            record for record in payload["classes"] if record["canonical_mask"] == h0
        )
        record["count"] += 1
        self.assert_rejected(payload)

    def test_parameter_mutation_is_rejected(self) -> None:
        payload = copy.deepcopy(self.payload)
        payload["parameters"]["h11"] -= 4
        self.assert_rejected(payload)

    def test_h11_integrality_gate(self) -> None:
        with self.assertRaises(ValueError):
            exact_check.published_hamiltonian_counts(705, 2819)

    def test_source_n_masks_cover_six_census(self) -> None:
        self.assertEqual(set(exact_check.SOURCE_N_MASKS), set(self.model["classes6"]))


if __name__ == "__main__":
    unittest.main()
