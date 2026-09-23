"""Hostile clean-room tests for the sealed Wave141 package."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import independent_verify as verify  # noqa: E402


class IndependentWave141Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = verify.build_results()

    def test_final_discovery_manifest_and_prerequisites(self) -> None:
        package = self.result["sealed_package"]
        self.assertEqual(
            package["manifest_sha256"],
            verify.SEALED_DISCOVERY_MANIFEST,
        )
        self.assertEqual(package["entry_count"], 9)
        self.assertTrue(package["manifest_pass"])
        self.assertTrue(package["entries_pass"])
        self.assertTrue(self.result["wave21_prerequisite"]["pass"])

    def test_two_independent_transform_controls(self) -> None:
        controls = self.result["bivariate_transform"]["small_controls"]
        self.assertEqual(
            [control["matrix"] for control in controls],
            ["adjacency(K3)", "adjacency(K5)"],
        )
        for control in controls:
            self.assertTrue(control["symmetric"])
            self.assertTrue(control["even_rows"])
            self.assertTrue(control["idempotent_mod_2"])
            self.assertTrue(control["kills_one"])
            self.assertTrue(control["input_marginals_pass"])
            self.assertTrue(control["output_marginals_pass"])
            self.assertTrue(control["output_even_pass"])
            self.assertTrue(control["input_complement_pass"])
            self.assertTrue(control["transform_pass"])

    def test_small_direct_ranks_match_d8_formula(self) -> None:
        for control in self.result["bivariate_transform"]["small_controls"]:
            self.assertEqual(
                control["direct_transform_rank_even_output"],
                control["expected_transform_rank_even_output"],
            )
            self.assertEqual(
                control["direct_transform_rank_after_complement"],
                control["expected_transform_rank_after_complement"],
            )

    def test_target_d8_dimension_and_ranks(self) -> None:
        d8 = self.result["bivariate_transform"]["D8"]
        self.assertEqual(d8["invariant_dimension"], 1275)
        self.assertEqual(d8["combined_equality_rank"], 3725)
        self.assertEqual(d8["additional_rank_after_input_complement"], 1225)
        self.assertEqual(sum(d8["Burnside_traces"].values()), 8 * 1275)

    def test_graph_classes_and_decks_reconstruct(self) -> None:
        alignment = self.result["locally_admissible_alignment"]
        self.assertEqual(alignment["class_counts"], {"4": 9, "5": 21, "6": 62})
        self.assertTrue(all(alignment["mapping_bijections"].values()))
        self.assertTrue(alignment["four_to_five_decks_pass"])
        self.assertTrue(alignment["five_to_six_decks_pass"])
        self.assertEqual(
            alignment["N23_repair"],
            {"row": 7, "column": 23, "corrected_column_sum": 6},
        )

    def test_n3_mapping_and_sign(self) -> None:
        n3 = self.result["locally_admissible_alignment"]["N3"]
        self.assertEqual(n3["source_index"], 3)
        self.assertEqual(n3["canonical_mask"], 5941)
        self.assertEqual(n3["edge_count"], 8)
        self.assertEqual(len(n3["triangles"]), 2)
        self.assertEqual(len(n3["cross_edges"]), 2)
        self.assertTrue(n3["cross_edges_form_matching"])
        self.assertEqual(n3["signed_shell_sign"], 1)

    def test_signed_shells_and_affine_cancellation(self) -> None:
        signed = self.result["signed_rows"]
        expected = {
            "0": ("1", "0"),
            "1": ("-99", "0"),
            "2": ("3465", "0"),
            "3": ("-56595", "0"),
            "4": ("462924", "0"),
            "5": ("-1821204", "0"),
            "6": ("2024484", "512/3"),
        }
        for order, pair in expected.items():
            self.assertEqual(
                (
                    signed["shells"][order]["constant"],
                    signed["shells"][order]["n3_coefficient"],
                ),
                pair,
            )
        cancellation = signed["affine_cancellation"]
        self.assertEqual(cancellation["positive_constant_sum"], "561276870")
        self.assertEqual(cancellation["negative_constant_sum"], "-559252386")
        self.assertEqual(cancellation["slope_total"], "512/3")

    def test_exact_low_rows_are_derived_not_assumed(self) -> None:
        rows = self.result["exact_low_rows"]["rows"]
        self.assertEqual(rows["0"], {"0": 1})
        self.assertEqual(rows["1"], {"14": 99})
        self.assertEqual(rows["2"], {"24": 4158, "26": 693})
        self.assertEqual(
            rows["3"],
            {"30": 70686, "32": 41580, "34": 36036, "36": 8547},
        )

    def test_n3_has_output_weight_56_but_no_cell_identity(self) -> None:
        detail = self.result["N3_output_detail"]
        self.assertEqual(
            detail["outside_neighbor_profile"],
            {"0": 33, "1": 52, "2": 8},
        )
        self.assertEqual(detail["output_weight_wt_A1S"], 56)
        self.assertTrue(detail["N3_sign_matches"])
        self.assertEqual(
            self.result["scope_boundary"]["full_output_weight_by_six_vertex_class"],
            "NOT_DERIVED",
        )

    def test_nonnegativity_bound_is_weaker(self) -> None:
        bound = self.result["nonnegativity_only_bound"]
        self.assertEqual(bound["rational_upper"], "838878579/128")
        self.assertEqual(bound["integer_upper"], 6553738)
        self.assertEqual(bound["multiple_of_3_upper"], 6553737)
        self.assertFalse(bound["improves_known_upper"])

    def test_numeric_scout_is_non_evidence_and_status_stays_unknown(self) -> None:
        scout = self.result["numerical_scout"]
        self.assertEqual(scout["evidentiary_status"], "NONE")
        self.assertFalse(scout["accepted_as_feasible"])
        self.assertFalse(scout["accepted_as_infeasible"])
        self.assertTrue(self.result["discovery_exact_projection_matches"])
        self.assertEqual(
            self.result["scope_boundary"]["formal_rational_feasibility"],
            "UNKNOWN",
        )
        self.assertEqual(self.result["scope_boundary"]["Conway_99"], "UNKNOWN")


if __name__ == "__main__":
    unittest.main()
