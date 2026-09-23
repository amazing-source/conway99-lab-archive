from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

import independent_verify as verify


HERE = Path(__file__).resolve().parent


class Wave94IndependentTests(unittest.TestCase):
    def test_frozen_inputs_and_dependency_manifests(self) -> None:
        result = verify.verify_frozen_inputs()
        self.assertTrue(result["passed"], result["failures"])
        self.assertEqual(result["discovery_files"], 10)
        self.assertEqual(result["discovery_manifest_entries"], 9)

    def test_seed_and_transition_multiplicities(self) -> None:
        self.assertEqual(len(verify.SEEDS), 560)
        rows = verify.TRANSITION_CANDIDATES
        mate_rows = [row for row in rows if verify.mate(row[1]) == row[2]]
        nonmate_rows = [row for row in rows if verify.mate(row[1]) != row[2]]
        self.assertEqual((len(mate_rows), len(nonmate_rows)), (84, 840))
        self.assertEqual(
            {verify.transition_seed_multiplicity(row) for row in mate_rows},
            {0},
        )
        self.assertEqual(
            {verify.transition_seed_multiplicity(row) for row in nonmate_rows},
            {8},
        )

    def test_all_local_matchings_and_cap(self) -> None:
        result = verify.local_matching_census()
        self.assertEqual(result["perfect_matchings_on_twelve"], 10395)
        self.assertEqual(
            set(result["forbidden_pair_count_census"]),
            {"0", "1", "2", "3", "4", "6"},
        )
        self.assertNotIn("5", result["forbidden_pair_count_census"])
        self.assertEqual(
            result["maximum_selected_pairs_in_one_local_seed_section"],
            1,
        )

    def test_global_seed_cap_is_sharp(self) -> None:
        transitions = verify.selection_saturating_seed(verify.SEEDS[0])
        result = verify.analyze_selected_transitions(transitions)
        self.assertTrue(result["passed"])
        self.assertEqual(result["maximum_seed_load"], 4)
        # A cap of three would reverse the required incidence inequality.
        self.assertGreater(result["maximum_seed_load"], 3)

    def test_mixed_local_profiles_obey_incidence_bound(self) -> None:
        profile = [0, 1, 2, 3, 4, 6, 0, 1, 2, 3, 4, 6, 0, 1]
        result = verify.analyze_selected_transitions(
            verify.selection_from_profile(profile)
        )
        self.assertTrue(result["passed"])
        self.assertEqual(result["f"], sum(profile))
        self.assertEqual(
            result["transition_seed_incidences"],
            8 * (84 - sum(profile)),
        )
        self.assertLessEqual(
            result["transition_free_seeds"],
            392 + 2 * sum(profile),
        )

    def test_rejects_nonmatching_transition_selection(self) -> None:
        valid = list(verify.selection_from_profile([0] * 14))
        valid[-1] = valid[0]
        with self.assertRaises(ValueError):
            verify.validate_selected_transitions(valid)

    def test_prism_root_multiplicity_and_c4_weights(self) -> None:
        result = verify.prism_identity()
        self.assertTrue(result["passed"])
        self.assertEqual(result["rooted_transitions_in_one_prism"], 6)
        self.assertEqual(
            result["C4_count_by_cross_matching_size"],
            {"0": 0, "1": 0, "2": 1, "3": 3},
        )
        # Counting only five roots would not give the claimed 12P term.
        self.assertNotEqual(2 * 5, 12)

    def test_complementary_fano_seed_injection_controls(self) -> None:
        result = verify.norm14_seed_map()
        self.assertTrue(result["passed"])
        self.assertEqual(result["support_spectral_edge_upper"], 31)
        self.assertEqual(result["same_sign_edges_forced"], 0)
        self.assertEqual(result["design_pair_incidences"], 42)
        self.assertEqual(result["common_neighbor_pair_capacity"], 42)
        self.assertTrue(result["root_pair_saturation"])

    def test_orientation_counts_both_signs_exactly_once(self) -> None:
        result = verify.global_arithmetic()
        self.assertTrue(result["N14_counts_both_signs"])
        self.assertEqual(result["positive_roots_in_test_sign_pair"], [7, 7])
        self.assertEqual(result["test_sign_pair_total"], 14)
        self.assertEqual(result["test_sign_pair_total"], 7 * 2)

    def test_floor_and_all_compatible_identity_rows(self) -> None:
        result = verify.global_arithmetic()
        self.assertTrue(result["passed"])
        self.assertEqual(result["full_identity_domain_rows_checked"], 1387)
        expected = {4158: 5544, 4155: 5545, 708: 7515, 0: 7920}
        for n3, bound in expected.items():
            self.assertEqual(verify.bound_from_n3(n3), bound)
            prisms = (4158 - n3) // 3
            self.assertEqual(verify.bound_from_prisms(prisms), bound)
        with self.assertRaises(ValueError):
            verify.bound_from_n3(4157)
        with self.assertRaises(ValueError):
            verify.bound_from_n3(-3)
        with self.assertRaises(ValueError):
            verify.bound_from_prisms(1387)

    def test_discovery_comparison_and_fail_closed_scope(self) -> None:
        result = verify.build_results()
        self.assertEqual(result["verdict"], "VERIFIED")
        self.assertTrue(result["discovery_comparison"]["passed"])
        self.assertIsNone(result["status"]["N16_upper_bound"])
        self.assertIsNone(result["status"]["N18_upper_bound"])
        self.assertIsNone(result["status"]["strict_n3_upper_bound"])
        self.assertEqual(result["status"]["Conway_99"], "UNKNOWN")

    def test_canonical_replay(self) -> None:
        canonical = HERE / "independent-results.json"
        self.assertEqual(
            canonical.read_bytes(),
            verify.canonical_bytes(verify.build_results()),
        )
        with tempfile.TemporaryDirectory() as temporary:
            copy = Path(temporary) / "result.json"
            copy.write_bytes(verify.canonical_bytes(verify.build_results()))
            payload = json.loads(copy.read_text(encoding="utf-8"))
            self.assertEqual(payload["claim_label"], "VERIFIED")


if __name__ == "__main__":
    unittest.main()
