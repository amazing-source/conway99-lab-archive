"""Hostile mutation tests for the independent Wave153 verifier."""

from __future__ import annotations

import copy
import sys
import unittest
from fractions import Fraction
from pathlib import Path


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import independent_verifier as verifier  # noqa: E402


class HostileMutationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        components = verifier.load_json(verifier.COMPONENTS_PATH)
        invariants = verifier.load_json(verifier.INVARIANTS_PATH)
        cls.results = verifier.load_gzip_json(verifier.RESULTS_PATH)
        cls.records = verifier.component_records(components)
        cls.rows_by_type = [verifier.adjacency(record) for record in cls.records]
        cls.action = verifier.reconstruct_action(cls.records)
        cls.orbits = verifier.reconstruct_orbits(
            components["component_type_triples"], cls.action
        )
        cls.orbit = cls.orbits[0]
        cls.target = verifier.target_pair_values(
            cls.orbit["type_triple"], cls.rows_by_type
        )
        allowed = verifier.allowed_pairs_by_type(cls.rows_by_type)
        cls.candidates = verifier.candidate_columns(
            cls.orbit["type_triple"], allowed, cls.target
        )
        cls.lane = cls.results["results"][0]
        verifier.verify_lane(cls.lane, 0, cls.orbit, cls.candidates, cls.target)
        cls.frozen_action = invariants["simultaneous_fibre_permutation_action"]

    def assert_rejected(self, lane: dict) -> None:
        with self.assertRaises(verifier.VerificationError):
            verifier.verify_lane(lane, 0, self.orbit, self.candidates, self.target)

    def test_numerator_mutation_rejected(self) -> None:
        lane = copy.deepcopy(self.lane)
        old = Fraction(lane["exact_witness"][0][1])
        lane["exact_witness"][0][1] = str(
            Fraction(old.numerator + 1, old.denominator)
        )
        self.assert_rejected(lane)

    def test_denominator_mutation_rejected(self) -> None:
        lane = copy.deepcopy(self.lane)
        old = Fraction(lane["exact_witness"][0][1])
        lane["exact_witness"][0][1] = str(
            Fraction(old.numerator, old.denominator + 1)
        )
        self.assert_rejected(lane)

    def test_candidate_index_mutation_rejected(self) -> None:
        lane = copy.deepcopy(self.lane)
        lane["exact_witness"][0][0] = len(self.candidates)
        self.assert_rejected(lane)

    def test_orbit_position_mutation_rejected(self) -> None:
        lane = copy.deepcopy(self.lane)
        lane["orbit_position"] = 1
        self.assert_rejected(lane)

    def test_coefficient_bound_mutation_rejected(self) -> None:
        lane = copy.deepcopy(self.lane)
        lane["exact_witness"][0][1] = "2"
        self.assert_rejected(lane)

    def test_duplicate_candidate_mutation_rejected(self) -> None:
        lane = copy.deepcopy(self.lane)
        lane["exact_witness"][1][0] = lane["exact_witness"][0][0]
        self.assert_rejected(lane)

    def test_noncanonical_rational_rejected(self) -> None:
        lane = copy.deepcopy(self.lane)
        lane["exact_witness"][0][1] = "2/4"
        self.assert_rejected(lane)

    def test_action_was_rebuilt_not_assumed(self) -> None:
        self.assertEqual(self.action, self.frozen_action)

    def test_live_manifests_verify(self) -> None:
        self.assertEqual(verifier.verify_manifest(verifier.PACKAGE_MANIFEST_PATH), 22)
        self.assertEqual(verifier.verify_manifest(verifier.INPUT_FREEZE_PATH), 6)


if __name__ == "__main__":
    unittest.main()
