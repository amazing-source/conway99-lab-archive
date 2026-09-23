#!/usr/bin/env python3
"""Focused adversarial tests for the independent Wave 18 checker."""

from __future__ import annotations

import importlib.util
import json
import sys
import unittest
from fractions import Fraction
from pathlib import Path


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "wave18_independent_checker",
    HERE / "independent_checker.py",
)
assert SPEC is not None and SPEC.loader is not None
CHECK = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = CHECK
SPEC.loader.exec_module(CHECK)


class IndependentWave18Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.results, cls.mutations = CHECK.build_results()

    def test_authenticated_inputs_and_attempts(self) -> None:
        self.assertEqual(
            CHECK.authenticate(CHECK.EXPECTED_INPUTS),
            CHECK.EXPECTED_INPUTS,
        )
        self.assertEqual(
            CHECK.authenticate(CHECK.SUBMITTED_ARTIFACTS),
            CHECK.SUBMITTED_ARTIFACTS,
        )

    def test_two_q_enumerators_agree_on_nine_profiles(self) -> None:
        profiles_a = CHECK.q_profiles_by_counts()
        profiles_b = CHECK.q_profiles_reference()
        self.assertEqual(profiles_a, profiles_b)
        self.assertEqual(len(profiles_a), 9)
        self.assertEqual(
            [len(profile) for profile in profiles_a],
            [14, 15, 16, 17, 17, 17, 18, 18, 19],
        )
        self.assertTrue(all(sum(profile) == 38 for profile in profiles_a))
        self.assertTrue(
            all(min(CHECK.dk_values(profile)) >= 4 for profile in profiles_a)
        )

    def test_dk_three_obstruction_and_hostile_relaxation(self) -> None:
        certificate = CHECK.reconstruct_dk_three_obstruction()
        self.assertEqual(
            certificate["outcome"],
            "d_K=3 impossible, hence d_K>=4",
        )
        baseline = set(CHECK.q_profiles_by_counts(min_dk=4))
        relaxed = set(CHECK.q_profiles_by_counts(min_dk=3))
        self.assertEqual(len(relaxed - baseline), 4)

    def test_endpoint_crossings_for_all_point_sizes(self) -> None:
        summaries = CHECK.all_endpoint_summaries()
        expected_disjoint = {
            (2, 2): [0, 4],
            (2, 3): [0, 4],
            (2, 4): [0, 4],
            (2, 5): [0, 4],
            (3, 3): [0, 4, 6],
            (3, 4): [0, 4, 6],
            (3, 5): [0, 4, 6],
            (4, 4): [0, 4, 6, 8],
            (4, 5): [0, 4, 6, 8],
            (5, 5): [0, 4, 6, 8, 10],
        }
        for pair, edge_counts in expected_disjoint.items():
            self.assertEqual(
                summaries[f"disjoint_{pair[0]}x{pair[1]}"]["edge_counts"],
                edge_counts,
            )
        self.assertEqual(
            summaries["meeting_2x5_after_deletion"]["edge_counts"],
            [0],
        )
        self.assertEqual(
            summaries["meeting_3x5_after_deletion"]["edge_counts"],
            [0, 4],
        )
        self.assertEqual(
            summaries["meeting_4x5_after_deletion"]["edge_counts"],
            [0, 4, 6],
        )
        self.assertEqual(
            summaries["meeting_5x5_after_deletion"]["edge_counts"],
            [0, 4, 6, 8],
        )

    def test_size_two_fixed_sum_cases_and_actual_neighbors(self) -> None:
        expected_degree = {
            (2, 2): 6,
            (2, 3): None,
            (2, 4): 7,
            (3, 3): 7,
            (3, 4): None,
            (4, 4): 8,
        }
        for pair, degree in expected_degree.items():
            result = CHECK.size_two_fixed_sum(*pair)
            self.assertEqual(result.get("minimum_induced_degree"), degree)
            if degree is not None:
                self.assertEqual(
                    result["identity_check"],
                    "distinct actual original-vertex neighbors",
                )

    def test_point_size_profiles_are_complete(self) -> None:
        self.assertEqual(
            CHECK.point_size_profiles(54, 27),
            ((2,) * 27,),
        )
        self.assertEqual(
            CHECK.point_size_profiles(57, 27),
            (
                (2,) * 26 + (5,),
                (2,) * 25 + (3, 4),
                (2,) * 24 + (3, 3, 3),
            ),
        )
        self.assertEqual(
            CHECK.point_size_profiles(57, 28),
            ((2,) * 27 + (3,),),
        )

    def test_dense_subset_threshold_and_strictness(self) -> None:
        self.assertEqual(CHECK.smallest_subset_size_for_delta_six(), 27)
        self.assertLess(CHECK.spectral_gap_from_delta_six(26), 0)
        self.assertEqual(CHECK.spectral_gap_from_delta_six(27), 0)
        self.assertGreater(CHECK.spectral_gap_from_delta_six(28), 0)
        self.assertEqual(CHECK.spectral_upper_degree_sum(27), Fraction(162))

    def test_every_r18_branch_contradicts(self) -> None:
        self.assertEqual(self.results["r18"]["point_sizes"], "2^27")
        self.assertEqual(
            [branch["outcome"] for branch in self.results["r18"]["branches"]],
            ["contradiction", "contradiction"],
        )
        self.assertEqual(
            self.results["r18"]["branches"][0]["local_2_4_minimum_degree"],
            7,
        )
        self.assertEqual(
            self.results["r18"]["branches"][1]["odd_label_required_degree"],
            3,
        )

    def test_every_r19_m27_and_m28_branch_contradicts(self) -> None:
        r19 = self.results["r19"]
        self.assertEqual(
            [branch["outcome"] for branch in r19["m27_branches"]],
            ["contradiction", "contradiction", "contradiction"],
        )
        self.assertEqual(
            r19["m27_branches"][2]["fixed_sum_maximum"],
            8,
        )
        m28 = r19["m28_branch"]
        self.assertEqual(m28["size3_minimum_degree"], 9)
        self.assertEqual(m28["parity_adjusted_degree_sum_lower"], 172)
        self.assertEqual(m28["spectral_maximum_even_integer"], 170)
        self.assertEqual(m28["outcome"], "contradiction")

    def test_neighbor_merge_and_split_are_rejected(self) -> None:
        self.assertIn(
            "merged presented neighbor identity",
            self.mutations["M16"]["evidence"]["rejection"],
        )
        self.assertIn(
            "physical neighbor identity",
            self.mutations["M17"]["evidence"]["rejection"],
        )

    def test_forbidden_imports_not_declared(self) -> None:
        audit = self.results["premise_reconstruction"][
            "declared_report_input_audit"
        ]
        self.assertFalse(audit["forbidden_input_path_present"])
        self.assertEqual(
            audit["declared_inputs"],
            [
                "AGENTS.md",
                "verification/2026-07-23-wave16-n3-51-structural-audit.md",
                "verification/2026-07-23-wave15-global-lift-audit.md",
            ],
        )
        valid, rejected = CHECK.validate_assumption_manifest(
            CHECK.ALLOWED_ASSUMPTION_NAMES,
        )
        self.assertTrue(valid)
        self.assertEqual(rejected, [])

    def test_all_twenty_four_hostile_mutations_detected(self) -> None:
        self.assertEqual(
            set(self.mutations),
            {f"M{index:02d}" for index in range(1, 25)},
        )
        self.assertTrue(all(
            mutation["status"] == "DETECTED"
            for mutation in self.mutations.values()
        ))
        self.assertTrue(self.results["hostile_mutations"]["all_detected"])

    def test_checked_in_json_summaries_match_live_results(self) -> None:
        checked = json.loads(
            (HERE / "checker-results.json").read_text(encoding="utf-8")
        )
        mutated = json.loads(
            (HERE / "mutation-results.json").read_text(encoding="utf-8")
        )
        self.assertEqual(
            checked["q_profile_canonical_sha256"],
            self.results["q_profile_canonical_sha256"],
        )
        self.assertEqual(
            checked["semantic_core_sha256"],
            self.results["semantic_core"]["sha256"],
        )
        self.assertEqual(
            checked["r19"]["m27_point_profile_sha256"],
            self.results["r19"]["m27_point_profile_sha256"],
        )
        self.assertEqual(
            checked["r19"]["m28_point_profile_sha256"],
            self.results["r19"]["m28_point_profile_sha256"],
        )
        self.assertEqual(checked["tests"]["hostile_mutations"], "24/24 DETECTED")
        self.assertEqual(mutated["status"], "24/24 DETECTED")
        self.assertEqual(
            mutated["canonical_sha256"],
            self.results["hostile_mutations"]["sha256"],
        )
        self.assertEqual(
            set(mutated["mutations"]),
            set(self.mutations),
        )

    def test_status_boundary(self) -> None:
        self.assertEqual(
            self.results["status"]["conditional_n3_57"],
            "EXCLUDED_VERIFIER_RESULT",
        )
        self.assertEqual(
            self.results["status"]["global_conway_99_target"],
            "UNKNOWN",
        )
        self.assertEqual(self.results["status"]["novelty"], "UNKNOWN")
        self.assertFalse(
            self.results["status"][
                "prospective_wave17_combination_used_as_premise"
            ],
        )


if __name__ == "__main__":
    unittest.main()
