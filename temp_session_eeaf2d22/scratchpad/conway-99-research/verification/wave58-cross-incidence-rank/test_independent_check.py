#!/usr/bin/env python3
"""Hostile tests for the Wave 58 clean-room verifier."""

from __future__ import annotations

import copy
import importlib.util
import json
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "wave58_independent_check", HERE / "independent_check.py"
)
assert SPEC and SPEC.loader
CHECK = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CHECK)


class Wave58IndependentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.discovery = json.loads(CHECK.DISCOVERY.read_text(encoding="utf-8"))
        cls.wave36 = json.loads(CHECK.WAVE36.read_text(encoding="utf-8"))
        cls.wave40 = json.loads(CHECK.WAVE40.read_text(encoding="utf-8"))
        cls.result = CHECK.run_checks(write_output=False)

    def verify_mutation(self, mutated: dict) -> None:
        with self.assertRaises(AssertionError):
            CHECK.verify_discovery(mutated, self.wave36, self.wave40)

    def test_baseline_verified_scoped(self) -> None:
        self.assertEqual(self.result["claim_label"], "VERIFIED")
        self.assertEqual(
            self.result["status_boundary"]["conway_99_status"], "UNKNOWN"
        )
        self.assertFalse(
            self.result["wording_audit"][
                "normalized_component_counts_are_isomorphism_counts"
            ]
        )

    def test_component_distributions(self) -> None:
        components = self.result["independent_replay"]["component_censuses"]
        self.assertEqual(components["m4"]["accepted"], 50)
        self.assertEqual(components["m6"]["accepted"], 34640)
        self.assertEqual(
            components["m6"]["C4_distribution"],
            CHECK.EXPECTED_M6_DISTRIBUTION,
        )

    def test_exact_sets_versus_bounds(self) -> None:
        ledger = self.result["independent_replay"]["component_specific_C4"]
        self.assertFalse(ledger["kappa_1"]["exact_attainable_set_claimed"])
        self.assertFalse(
            ledger["kappa_2_overall"]["exact_attainable_set_claimed"]
        )
        self.assertEqual(
            ledger["kappa_2_6_plus_6"]["exact_local_set"],
            list(range(17)) + [18],
        )
        self.assertEqual(
            ledger["kappa_3"]["exact_local_set"],
            [6, 8, 10, 12, 14, 16, 18],
        )

    def test_wave40_restricted_support(self) -> None:
        replay = self.result["independent_replay"]["wave40_replay"]
        self.assertEqual(replay["triangle_free_masks"], 37378)
        self.assertNotIn(13, replay["C4_distribution"])
        self.assertEqual(replay["component_profiles"], {"12+24": 37378})

    def test_gram_formula_mutation_rejected(self) -> None:
        bad = copy.deepcopy(self.discovery)
        bad["gram_identities"]["B_transpose_B"] = "12I-A_Y+J-A_Y^2"
        self.verify_mutation(bad)

    def test_rank_row_mutation_rejected(self) -> None:
        bad = copy.deepcopy(self.discovery)
        bad["kernel_and_rank_derivation"]["rows"][1]["rank_B"] = 34
        self.verify_mutation(bad)

    def test_m4_distribution_mutation_rejected(self) -> None:
        bad = copy.deepcopy(self.discovery)
        bad["component_structural_reduction"]["component_censuses"]["m4"][
            "C4_distribution"
        ]["4"] -= 1
        self.verify_mutation(bad)

    def test_m6_count_mutation_rejected(self) -> None:
        bad = copy.deepcopy(self.discovery)
        bad["component_structural_reduction"]["component_censuses"]["m6"][
            "accepted_connected_triangle_free_codegree_at_most_2"
        ] += 1
        self.verify_mutation(bad)

    def test_component_witness_mutation_rejected(self) -> None:
        bad = copy.deepcopy(self.discovery)
        witness = bad["component_structural_reduction"]["component_censuses"][
            "m4"
        ]["canonical_witness_by_C4"]["2"]
        witness["cross_12_permutation"][0] = witness[
            "cross_12_permutation"
        ][1]
        self.verify_mutation(bad)

    def test_kappa_bound_mutation_rejected(self) -> None:
        bad = copy.deepcopy(self.discovery)
        bad["component_structural_reduction"][
            "kappa2_partition_4_plus_8_C4_X_bounds"
        ] = [2, 23]
        self.verify_mutation(bad)

    def test_scalar_control_mutation_rejected(self) -> None:
        bad = copy.deepcopy(self.discovery)
        bad["component_structural_reduction"][
            "kappa3_aligned_scalar_control"
        ]["multiplicities"][0] += 1
        self.verify_mutation(bad)

    def test_wave40_count_mutation_rejected(self) -> None:
        bad = copy.deepcopy(self.discovery)
        bad["wave40_restricted_lift_replay"]["canonical_replay"][
            "triangle_free_masks"
        ] -= 1
        self.verify_mutation(bad)

    def test_prior_chronology_mutation_rejected(self) -> None:
        bad_prior = copy.deepcopy(self.wave36)
        bad_prior["claim_label"] = "DERIVED"
        with self.assertRaises(AssertionError):
            CHECK.gram_rank_and_chronology_checks(bad_prior)

    def test_status_inflation_rejected(self) -> None:
        bad = copy.deepcopy(self.discovery)
        bad["result"]["endpoint"] = "EXCLUDED"
        self.verify_mutation(bad)


if __name__ == "__main__":
    unittest.main()
