from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

import static_compare


class Wave34RootedStructuralStaticComparisonTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = static_compare.build_result(full_census=True)

    def test_01_release_and_stage1_integrity(self) -> None:
        integrity = self.result["input_integrity"]
        self.assertTrue(integrity["all_hashes_pass"])
        self.assertEqual(
            integrity["candidate_inner_manifest"]["entry_count"],
            5,
        )
        self.assertEqual(integrity["stage1_manifest"]["entry_count"], 8)
        self.assertTrue(integrity["stage1_manifest"]["all_entries_pass"])

    def test_02_candidate_code_is_static_only(self) -> None:
        review = self.result["static_candidate_review"]
        self.assertFalse(review["candidate_code_imported"])
        self.assertFalse(review["candidate_code_executed"])
        self.assertEqual(review["static_test_method_count"], 7)
        self.assertEqual(
            review["files"]["reduction.py"][
                "direct_eval_exec_compile_import_calls"
            ],
            [],
        )
        self.assertEqual(
            review["files"]["check_results.py"]["exec_module_calls"],
            1,
        )

    def test_03_exact_wave33_coordinate_binding(self) -> None:
        binding = self.result["coordinate_binding"]
        self.assertEqual(binding["isomorphism_count"], 168)
        self.assertEqual(
            binding["chosen_point_map_candidate_to_wave33"],
            [0, 1, 3, 2, 5, 6, 4],
        )
        self.assertEqual(
            binding["chosen_line_map_candidate_to_wave33"],
            [0, 3, 5, 6, 2, 4, 1],
        )
        self.assertTrue(binding["support_adjacency_entrywise_match"])
        self.assertTrue(binding["support_to_O_entrywise_match"])

    def test_04_snf_has_independent_unit_witness(self) -> None:
        snf = self.result["snf"]
        self.assertEqual(snf["rank_over_Q_wave33_coordinates"], 13)
        self.assertEqual(snf["kernel_dimension"], 57)
        self.assertEqual(
            snf["snf_nonzero_invariant_factors"],
            [1] * 13,
        )
        self.assertEqual(abs(snf["verifier_unit_minor"]["determinant"]), 1)
        self.assertEqual(
            abs(snf["candidate_unit_minor_mapped_wave33_determinant"]),
            1,
        )

    def test_05_independent_two_factor_counts(self) -> None:
        census = self.result["two_factor_verification"]
        self.assertEqual(
            census["line_side_transfer"],
            {
                "underlying_total": 4_946_952,
                "labeled_total": 574_118_037,
                "cached_states": 1090,
            },
        )
        matching = census["matching_pair_census"]
        self.assertEqual(matching["labeled_total"], 574_118_037)
        self.assertEqual(matching["underlying_total"], 4_946_952)
        self.assertEqual(len(matching["labeled_cycle_census"]), 15)
        self.assertEqual(
            matching["labeled_cycle_census"]["7"],
            262_332_336,
        )
        self.assertEqual(
            matching["labeled_cycle_census"]["1+1+1+1+1+1+1"],
            24,
        )

    def test_06_fixed_action_and_C_bind_exactly(self) -> None:
        fixed = self.result["fixed_action_and_integral_C"]
        self.assertEqual(fixed["rank_P_F"], 13)
        self.assertEqual(fixed["trace_H_R"], -3)
        self.assertTrue(fixed["F_H_R_equals_C_SO"])
        self.assertTrue(fixed["C_binding_entrywise_match"])
        self.assertEqual(
            fixed["candidate_order_hashes"]["fixed_C_sha256"],
            "9bf08bdd279a7c1fc4267e70d4c448afa5063d78e245c0cf970f53ab3c0e9e69",
        )

    def test_07_projector_equivalence_both_directions(self) -> None:
        audit = self.result["projector_equivalence"]
        self.assertTrue(
            audit["forward"]["from_six_blocks_to_rank16_projector"]
        )
        self.assertEqual(audit["forward"]["rank"], 16)
        self.assertTrue(
            audit["reverse"]["all_six_blocks_reconstructed"]
        )
        self.assertEqual(audit["grassmann_dimension"], 432)
        self.assertEqual(
            audit["notation_map"]["candidate_rank16_E"],
            "Stage1 E_minus_4",
        )

    def test_08_integral_diagonal_and_modular_claims(self) -> None:
        fixed = self.result["fixed_action_and_integral_C"]
        self.assertEqual(
            fixed["solution_L_diagonal"],
            {
                "support_edge_completion": 30,
                "support_cross_nonedge_completion": 36,
            },
        )
        self.assertEqual(fixed["trace_L"], 2352)
        self.assertEqual(fixed["C_mod_7_rank"], 5)
        self.assertTrue(fixed["C_mod_7_square_zero"])
        comparison = self.result["candidate_result_comparison"]["checks"]
        self.assertTrue(comparison["mod3"])
        self.assertTrue(comparison["mod7"])

    def test_09_stage1_pair_census_refines_column_scope(self) -> None:
        reconciliation = self.result["stage1_reconciliation"]
        self.assertEqual(
            reconciliation["candidate_count_verified"],
            574_118_037,
        )
        self.assertEqual(
            reconciliation["duplicate_free_Pb_columns_surviving_rule"],
            448_879_368,
        )
        self.assertEqual(
            reconciliation[
                "Pb_only_columns_excluded_by_duplicate_pair_rule"
            ],
            125_238_669,
        )
        self.assertEqual(
            reconciliation["necessary_full_solution_single_column_types"],
            ["7", "5+2", "4+3", "3+2+2"],
        )
        self.assertEqual(
            reconciliation["classification"],
            "SCOPE_REFINEMENT_NOT_DISCREPANCY",
        )

    def test_10_candidate_comparison_and_scope_wall(self) -> None:
        comparison = self.result["candidate_result_comparison"]
        self.assertTrue(comparison["all_checks_pass"])
        self.assertEqual(comparison["material_discrepancies"], [])
        self.assertTrue(all(self.result["scope_checks"].values()))
        status = self.result["status"]
        self.assertEqual(
            status["released_structural_reparameterization"],
            "VERIFIED",
        )
        for key in (
            "binary_solution",
            "complete_exclusion",
            "rooted_graph_extension",
            "rooted_endpoint",
            "n3_708",
            "Conway_99",
            "novelty",
        ):
            self.assertEqual(status[key], "UNKNOWN")

    def test_11_deterministic_lf_json(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            first = Path(directory) / "first.json"
            second = Path(directory) / "second.json"
            static_compare.write_json_lf(first, self.result)
            static_compare.write_json_lf(second, self.result)
            self.assertEqual(first.read_bytes(), second.read_bytes())
            self.assertNotIn(b"\r\n", first.read_bytes())
            self.assertEqual(json.loads(first.read_text("utf-8")), self.result)


if __name__ == "__main__":
    unittest.main()
