#!/usr/bin/env python3
"""Hostile mutation tests for the independent Wave-22 verifier."""

from __future__ import annotations

import copy
import json
import unittest

import independent_verify as verifier


class IndependentVerifierTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.context = verifier.build_context()
        cls.witness = json.loads(verifier.WITNESS_PATH.read_text(encoding="utf-8"))

    def assert_rejected(self, mutation) -> None:
        altered = copy.deepcopy(self.witness)
        mutation(altered)
        with self.assertRaises(verifier.VerificationError):
            verifier.validate_witness_data(altered, self.context)

    def assert_rejected_with(self, mutation, pattern: str) -> None:
        altered = copy.deepcopy(self.witness)
        mutation(altered)
        with self.assertRaisesRegex(verifier.VerificationError, pattern):
            verifier.validate_witness_data(altered, self.context)

    def test_01_frozen_witness_passes(self) -> None:
        result = verifier.validate_witness_data(self.witness, self.context)
        self.assertEqual(result["deletion_rows_passed"], 62)
        self.assertEqual(result["hamiltonian_counts_passed"], 19)
        self.assertEqual(result["support_size"], 105)

    def test_02_independent_census_constants(self) -> None:
        self.assertEqual(self.context.six_census.total_unlabeled_classes, 156)
        self.assertEqual(len(self.context.six_census.admissible_representatives), 62)
        self.assertEqual(self.context.seven_census.total_unlabeled_classes, 1044)
        self.assertEqual(len(self.context.seven_census.admissible_representatives), 208)
        self.assertEqual(self.context.seven_census.admissible_labeled_masks, 394020)

    def test_03_deletion_column_sums(self) -> None:
        for column in range(208):
            self.assertEqual(sum(row[column] for row in self.context.deck), 7)

    def test_04_finite_field_ranks(self) -> None:
        self.assertEqual(self.context.ranks, {2: 48, 3: 57, 5: 61, 7: 61, 11: 62})

    def test_05_hamiltonian_alignment_and_values(self) -> None:
        self.assertEqual(len(set(self.context.figure_masks)), 19)
        self.assertEqual(
            set(self.context.figure_masks), set(self.context.hamiltonian_class_masks)
        )
        self.assertEqual(
            self.context.hamiltonian_values,
            (
                1237530,
                930270,
                1013430,
                163500,
                163500,
                81750,
                160680,
                78930,
                321360,
                160680,
                1410,
                2820,
                4158,
                1410,
                2820,
                1410,
                1410,
                3453,
                0,
            ),
        )

    def test_06_reject_missing_class(self) -> None:
        self.assert_rejected(lambda data: data["classes"].pop())

    def test_07_reject_extra_class(self) -> None:
        self.assert_rejected(lambda data: data["classes"].append({"canonical_mask": 1, "count": 0}))

    def test_08_reject_duplicate_mask(self) -> None:
        self.assert_rejected(
            lambda data: data["classes"][1].__setitem__(
                "canonical_mask", data["classes"][0]["canonical_mask"]
            )
        )

    def test_09_reject_noncanonical_mask(self) -> None:
        self.assert_rejected(
            lambda data: data["classes"][1].__setitem__("canonical_mask", 2)
        )

    def test_10_reject_reordered_classes(self) -> None:
        def mutate(data):
            data["classes"][0], data["classes"][1] = (
                data["classes"][1],
                data["classes"][0],
            )

        self.assert_rejected(mutate)

    def test_11_reject_negative_count(self) -> None:
        self.assert_rejected(lambda data: data["classes"][0].__setitem__("count", -1))

    def test_12_reject_string_count(self) -> None:
        self.assert_rejected(
            lambda data: data["classes"][0].__setitem__("count", "0")
        )

    def test_13_reject_boolean_count(self) -> None:
        self.assert_rejected(
            lambda data: data["classes"][0].__setitem__("count", False)
        )

    def test_14_reject_float_count(self) -> None:
        self.assert_rejected(
            lambda data: data["classes"][0].__setitem__("count", 0.0)
        )

    def test_15_reject_incremented_count(self) -> None:
        self.assert_rejected(
            lambda data: data["classes"][0].__setitem__(
                "count", data["classes"][0]["count"] + 1
            )
        )

    def test_16_reject_targeted_hamiltonian_change(self) -> None:
        mask = self.context.figure_masks[0]
        index = next(
            index
            for index, record in enumerate(self.witness["classes"])
            if record["canonical_mask"] == mask
        )
        hamiltonian = set(self.context.figure_masks)
        compensating_index = next(
            candidate
            for candidate, record in enumerate(self.witness["classes"])
            if record["canonical_mask"] not in hamiltonian and record["count"] > 0
        )

        def mutate(data):
            data["classes"][index]["count"] += 1
            data["classes"][compensating_index]["count"] -= 1

        self.assert_rejected_with(mutate, "Hamiltonian")

    def test_17_reject_zero_H18_changed_to_one(self) -> None:
        mask = self.context.figure_masks[18]
        index = next(
            index
            for index, record in enumerate(self.witness["classes"])
            if record["canonical_mask"] == mask
        )
        self.assertEqual(self.witness["classes"][index]["count"], 0)
        self.assert_rejected_with(
            lambda data: data["classes"][index].__setitem__("count", 1),
            "Hamiltonian",
        )

    def test_18_reject_n3_mutation(self) -> None:
        self.assert_rejected(lambda data: data["parameters"].__setitem__("n3", 708))

    def test_19_reject_h11_mutation(self) -> None:
        self.assert_rejected(
            lambda data: data["parameters"].__setitem__("h11", 2816)
        )

    def test_20_reject_n_mutation(self) -> None:
        self.assert_rejected(lambda data: data["parameters"].__setitem__("n", 100))

    def test_21_reject_boolean_parameter(self) -> None:
        self.assert_rejected(lambda data: data["parameters"].__setitem__("n3", True))

    def test_22_reject_parameter_extra_key(self) -> None:
        self.assert_rejected(lambda data: data["parameters"].__setitem__("extra", 0))

    def test_23_reject_wrong_class_record_schema(self) -> None:
        self.assert_rejected(lambda data: data["classes"][0].__setitem__("extra", 0))

    def test_24_reject_nonobject_class_record(self) -> None:
        self.assert_rejected(lambda data: data["classes"].__setitem__(0, [0, 0]))

    def test_25_reject_missing_classes_key(self) -> None:
        self.assert_rejected(lambda data: data.pop("classes"))

    def test_26_reject_total_preserving_nonhamiltonian_deck_mutation(self) -> None:
        hamiltonian = set(self.context.figure_masks)
        donor = next(
            index
            for index, record in enumerate(self.witness["classes"])
            if record["canonical_mask"] not in hamiltonian and record["count"] > 0
        )
        donor_column = tuple(row[donor] for row in self.context.deck)
        receiver = next(
            index
            for index, record in enumerate(self.witness["classes"])
            if record["canonical_mask"] not in hamiltonian
            and tuple(row[index] for row in self.context.deck) != donor_column
        )

        def mutate(data):
            data["classes"][donor]["count"] -= 1
            data["classes"][receiver]["count"] += 1

        self.assert_rejected_with(mutate, "deletion equations")


if __name__ == "__main__":
    unittest.main()
