#!/usr/bin/env python3
"""Adversarial unit checks for the Wave153 discovery package."""

from __future__ import annotations

import importlib.util
import sys
import unittest
from fractions import Fraction
from pathlib import Path


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "wave153_correlation", HERE / "correlation_polytope.py"
)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class Wave153Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.frozen = MODULE.load_inputs()
        cls.artifact = MODULE.read_gzip(HERE / "exact-results.json.gz")

    def lane_data(self, position):
        types, representatives, _, _ = self.frozen
        row = self.artifact["results"][position]
        orbit = representatives[position]
        records = [types[index] for index in row["type_triple"]]
        gram = MODULE.target_gram(records)
        candidates = MODULE.candidate_columns(records)
        witness = MODULE.decode_witness(row["exact_witness"])
        return row, orbit, candidates, gram, witness

    def test_frozen_dimensions_and_transfer(self):
        types, representatives, prior_indices, context = self.frozen
        self.assertEqual(len(types), 18)
        self.assertEqual(len(representatives), 275)
        self.assertEqual(len(prior_indices), 74)
        self.assertEqual(len(context["survivor_by_index"]), 1140)
        transferred = {
            index
            for orbit in representatives
            for index in orbit["triple_indices"]
        }
        self.assertEqual(transferred, set(context["survivor_by_index"]))

    def test_artifact_scope_and_coverage(self):
        artifact = self.artifact
        self.assertEqual(artifact["claim_label"], "CANDIDATE")
        self.assertEqual(
            artifact["coverage"]["representatives_with_exact_witnesses"], 275
        )
        self.assertEqual(
            artifact["coverage"]["unordered_type_triples"], 1140
        )
        self.assertEqual(
            artifact["result"]["binary_incidence_design"], "UNKNOWN"
        )
        self.assertEqual(
            artifact["result"]["strict_n3_upper_bound"], "NOT_OBTAINED"
        )
        self.assertEqual(artifact["result"]["Conway_99"], "UNKNOWN")

    def test_selected_exact_replays(self):
        for position in [0, 137, 274]:
            with self.subTest(position=position):
                row, orbit, candidates, gram, witness = self.lane_data(
                    position
                )
                self.assertEqual(row["orbit_position"], position)
                self.assertEqual(row["type_triple"], orbit["type_triple"])
                replay = MODULE.replay_witness(candidates, gram, witness)
                self.assertEqual(
                    replay["support"], row["exact_replay"]["support"]
                )
                self.assertEqual(replay["total_weight"], "60")

    def test_mutated_numerator_fails_closed(self):
        _, _, candidates, gram, witness = self.lane_data(0)
        index, value = witness[0]
        hostile = list(witness)
        hostile[0] = (
            index,
            Fraction(value.numerator + 1, value.denominator),
        )
        with self.assertRaises(AssertionError):
            MODULE.replay_witness(candidates, gram, hostile)

    def test_duplicate_candidate_fails_closed(self):
        _, _, candidates, gram, witness = self.lane_data(0)
        hostile = list(witness)
        hostile.append(witness[0])
        with self.assertRaisesRegex(AssertionError, "duplicate"):
            MODULE.replay_witness(candidates, gram, hostile)

    def test_out_of_range_candidate_fails_closed(self):
        _, _, candidates, gram, witness = self.lane_data(0)
        hostile = list(witness)
        hostile[0] = (len(candidates), hostile[0][1])
        with self.assertRaisesRegex(AssertionError, "candidate index"):
            MODULE.replay_witness(candidates, gram, hostile)

    def test_upper_bound_fails_closed(self):
        _, _, candidates, gram, witness = self.lane_data(0)
        hostile = list(witness)
        hostile[0] = (hostile[0][0], Fraction(2))
        with self.assertRaisesRegex(AssertionError, "outside"):
            MODULE.replay_witness(candidates, gram, hostile)

    def test_noncanonical_rational_fails_closed(self):
        with self.assertRaisesRegex(AssertionError, "noncanonical"):
            MODULE.decode_witness([[0, "2/2"]])


if __name__ == "__main__":
    unittest.main()
