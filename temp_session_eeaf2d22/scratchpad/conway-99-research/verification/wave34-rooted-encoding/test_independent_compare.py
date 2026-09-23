from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import independent_compare as audit


class TestIndependentComparison(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = audit.run()

    def test_precomparison_remains_byte_frozen(self) -> None:
        self.assertTrue(
            self.result["input_integrity"]["precomparison_manifest_unchanged"]
        )
        self.assertEqual(
            self.result["input_integrity"]["precomparison_manifest_sha256"],
            "3f1bdcb0ca2d08ee0380cd1435673fddb499db8c3a8273f6676c18f17ad3550c",
        )

    def test_candidate_manifests_and_gzip(self) -> None:
        integrity = self.result["input_integrity"]
        self.assertEqual(integrity["publication_manifest"]["entry_count"], 16)
        self.assertEqual(integrity["complete_local_manifest"]["entry_count"], 18)
        self.assertTrue(integrity["publication_is_consistent_subset"])
        gzip_result = self.result["gzip_audit"]
        self.assertTrue(gzip_result["exact_chunkwise_round_trip"])
        self.assertEqual(
            gzip_result["raw_sha256"],
            "2362d15f3a20df0a0d7745eb619a94061cee9911c8dda36c191fb6d728c1c3d3",
        )

    def test_canonical_label_binding(self) -> None:
        binding = self.result["canonical_label_binding"]
        self.assertEqual(
            binding["chosen_point_map_candidate_to_wave33"],
            [0, 1, 3, 2, 5, 6, 4],
        )
        self.assertEqual(
            binding["chosen_line_map_candidate_to_wave33"],
            list(range(7)),
        )
        self.assertEqual(binding["fano_isomorphism_count"], 168)
        self.assertTrue(binding["support_exact_under_map"])
        self.assertTrue(binding["incidence_exact_under_map"])
        self.assertTrue(binding["candidate_audit_fixed_hashes_match"])

    def test_every_clause_and_semantic_family(self) -> None:
        formula = self.result["formula_reconstruction"]
        self.assertTrue(formula["exact_byte_stream_match"])
        self.assertEqual(formula["variables"], 1_233_001)
        self.assertEqual(formula["clauses"], 4_323_943)
        self.assertEqual(
            formula["clause_length_histogram"],
            {"1": 12154, "2": 1828218, "3": 2483571},
        )
        self.assertEqual(
            formula["semantic_variable_records"], formula["variables"]
        )
        self.assertEqual(
            set(formula["families"]),
            {
                "primary_variables",
                "D_hollow",
                "D_symmetry",
                "D_row_weight_9",
                "B_row_weight_3",
                "SQ_block_FB_equals_2J",
                "SO_block_ASF_plus_FD",
                "OO_block_diagonal",
                "OO_block_offdiagonal",
                "OQ_block_DB",
                "QQ_block_column_weight_14",
                "QQ_block_pair_intersection_2",
            },
        )

    def test_primitive_gadgets_in_both_directions(self) -> None:
        gadgets = self.result["gadget_audit"]
        self.assertTrue(gadgets["AND_equivalence"])
        self.assertTrue(gadgets["exact_threshold_semantics"])
        self.assertTrue(gadgets["exact_CNF_existential_equivalence"])
        self.assertGreater(gadgets["exact_CNF_primary_assignments"], 0)

    def test_ordered_D_count_difference_is_exactly_gates(self) -> None:
        counts = self.result["count_comparison"]
        self.assertEqual(counts["semantic_independent_primary_bits"], 3465)
        self.assertEqual(counts["primary_variable_difference"], 2485)
        self.assertEqual(
            counts["difference_decomposition"],
            {
                "explicit_D_diagonal_variables": 70,
                "mirrored_offdiagonal_D_variables": 2415,
                "total": 2485,
            },
        )
        self.assertEqual(counts["total_clause_difference"], 4900)
        self.assertEqual(
            counts["clause_histogram_difference"],
            {"1": 70, "2": 4830, "3": 0},
        )
        self.assertTrue(counts["complete_domain_equivalence"])

    def test_model_map_and_checker_route(self) -> None:
        model = self.result["model_route_audit"]
        self.assertEqual(model["signature_models"], 13)
        self.assertEqual(model["primary_ids_distinguished"], 5950)
        self.assertTrue(model["D_mapping_exact"])
        self.assertTrue(model["B_mapping_exact"])
        self.assertTrue(model["hostile_control_rejected"])
        self.assertTrue(
            model["checker_block_failure_counts_match_independent"]
        )
        self.assertFalse(model["decoder_checks_dimacs_clauses"])

    def test_corrections_do_not_change_formula_verdict(self) -> None:
        corrections = self.result["corrections"]
        self.assertEqual(
            [item["id"] for item in corrections],
            ["W34-RC-V-001", "W34-RC-V-002", "W34-RC-V-003"],
        )
        self.assertTrue(
            all(item["formula_impact"].startswith("NONE") for item in corrections)
        )
        self.assertEqual(
            self.result["status"]["encoding_exact_scope"], "VERIFIED"
        )
        for unresolved in (
            "SAT",
            "UNSAT",
            "rooted_graph_extension",
            "rooted_endpoint",
            "n3_708",
            "Conway_99",
            "novelty",
        ):
            self.assertEqual(self.result["status"][unresolved], "UNKNOWN")

    def test_saved_machine_result_matches_fresh_run(self) -> None:
        saved = json.loads(
            (HERE / "comparison-results.json").read_text(encoding="utf-8")
        )
        self.assertEqual(saved, self.result)


if __name__ == "__main__":
    unittest.main()
