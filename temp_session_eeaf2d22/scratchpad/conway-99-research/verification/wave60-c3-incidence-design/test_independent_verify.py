#!/usr/bin/env python3
"""Tests for the structurally independent Wave 60 verifier."""

from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
SPEC = importlib.util.spec_from_file_location(
    "wave60_independent_verify", HERE / "independent_verify.py"
)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("cannot load independent verifier")
VERIFY = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VERIFY)


class Wave60IndependentVerificationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = VERIFY.reconstruct(REPO)

    def test_component_classification(self) -> None:
        self.assertEqual(
            self.result["component_classification"],
            {
                "coordinate_normalized": 216,
                "accepted": 50,
                "accepted_C4_distribution": {"2": 6, "4": 30, "6": 14},
                "fibre_preserving_types": 18,
            },
        )

    def test_safe_coordinate_orbits(self) -> None:
        reduction = self.result["safe_coordinate_reduction"]
        self.assertEqual(reduction["multisets"], 1140)
        self.assertEqual(reduction["simultaneous_fibre_orbits"], 275)
        self.assertEqual(
            reduction["orbit_size_distribution"], {"1": 15, "3": 145, "6": 115}
        )
        self.assertFalse(reduction["target_automorphism_assumed"])
        self.assertEqual(
            reduction["unsafe_independent_fibre_witness"],
            {
                "source": [0, 1, 1],
                "unsafe_independent_image": [0, 1, 11],
                "safe_orbit_size": 3,
            },
        )

    def test_f2_filter_is_exact_but_redundant(self) -> None:
        rank = self.result["f2_filter"]
        self.assertEqual(
            rank["target_rank_distribution"],
            {"14": 67, "16": 415, "18": 412, "20": 185, "22": 51, "24": 10},
        )
        self.assertEqual(rank["rejected_triples"], 0)
        self.assertEqual(rank["conclusion"], "REDUNDANT")

    def test_candidate_formula_matches_brute_force(self) -> None:
        support = self.result["candidate_support"]
        self.assertEqual(support["formal_patterns"], 21)
        self.assertEqual(support["pattern_classes"], {"AAA": 6, "ABB": 9, "BBB": 6})
        self.assertEqual(support["minimum_over_1140"], 15936)
        self.assertEqual(support["maximum_over_1140"], 27200)
        self.assertEqual(support["zero_support_triples"], 0)
        self.assertEqual(support["aligned_formula_count"], 20928)
        self.assertEqual(support["aligned_bruteforce_count"], 20928)
        self.assertEqual(
            set(support["aligned_pattern_counts"].values()), {64, 576, 784, 2352}
        )

    def test_local_constraints_force_omitted_equations(self) -> None:
        reduction = self.result["marginal_reduction"]
        self.assertEqual(reduction["local_pair_target_sum_per_component"], 60)
        self.assertEqual(reduction["local_pair_target_row_sums"], 10)
        self.assertEqual(
            reduction["category_target_multiplicities"],
            {"A0": 4, "A1": 4, "A2": 4, "B0": 16, "B1": 16, "B2": 16},
        )

    def test_hostile_mutations_are_detected(self) -> None:
        mutation = self.result["hostile_mutations"]
        self.assertTrue(mutation["triangle_injection_rejected"])
        self.assertTrue(mutation["wrong_fibre_pattern_rejected"])
        self.assertTrue(mutation["odd_diagonal_target_rejected_as_nonalternating"])
        self.assertTrue(mutation["unsafe_independent_fibre_action_not_used"])

    def test_search_telemetry_stays_unknown(self) -> None:
        status = self.result["bounded_search_status"]
        self.assertEqual(status["sat"], "UNKNOWN_NON_EVIDENTIARY")
        self.assertEqual(status["local_search"], "UNKNOWN_NON_EVIDENTIARY")
        self.assertEqual(self.result["endpoint_status"], "UNKNOWN")

    def test_discovery_manifest(self) -> None:
        self.assertGreaterEqual(self.result["discovery_manifest"]["entries_checked"], 20)
        self.assertEqual(self.result["discovery_manifest"]["failures"], [])


if __name__ == "__main__":
    unittest.main()
