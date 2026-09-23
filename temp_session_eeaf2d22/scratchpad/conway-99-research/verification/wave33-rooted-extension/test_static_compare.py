from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from pathlib import Path

import static_compare as compare


class Wave33StaticComparisonTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.results = compare.build_results()

    def test_release_inventory_and_precomparison_freeze(self) -> None:
        integrity = self.results["input_integrity"]
        self.assertTrue(integrity["all_hashes_pass"])
        self.assertEqual(integrity["candidate_release_inventory_entries"], 9)
        self.assertEqual(integrity["candidate_inner_manifest_entries"], 8)
        self.assertEqual(integrity["precomparison_manifest_entries"], 8)

    def test_candidate_inner_manifest_hash_correction(self) -> None:
        integrity = self.results["input_integrity"]
        correction = self.results["release_metadata_corrections"]["manifest_hash"]
        self.assertEqual(
            integrity["candidate_inner_manifest_sha256"],
            "153860d39fe7274a2f55ee952bcad1135cf4134ccc36d9aec07f6da379c5ca04",
        )
        self.assertEqual(correction["superseded_release_note"], "17f9...")

    def test_candidate_json_is_canonical_static_data(self) -> None:
        payload = compare.load_json_static(compare.CANDIDATE_RESULTS)
        self.assertEqual(
            compare.CANDIDATE_RESULTS.read_bytes(),
            compare.canonical_bytes(payload),
        )

    def test_candidate_code_was_only_parsed(self) -> None:
        review = self.results["candidate_static_code_review"]
        self.assertEqual(review["mode"], "AST_AND_TEXT_ONLY")
        self.assertFalse(review["candidate_code_imported"])
        self.assertFalse(review["candidate_code_executed"])
        self.assertEqual(review["test_method_count"], 15)
        self.assertEqual(review["exact_check"]["syntax_parse"], "PASS")
        self.assertEqual(review["exact_check"]["dynamic_execution_calls"], [])

    def test_notation_map_is_explicit(self) -> None:
        notation = self.results["semantic_comparison"][
            "notation_map_candidate_to_cleanroom"
        ]
        self.assertEqual(notation["A_S"], "F (support adjacency)")
        self.assertEqual(notation["F"], "D (support-to-O incidence)")
        self.assertEqual(notation["D"], "H (induced O adjacency)")
        self.assertEqual(notation["B"], "B (O-Q incidence)")

    def test_quotient_design_and_six_blocks_match(self) -> None:
        checks = self.results["semantic_comparison"]["checks"]
        self.assertTrue(checks["partition_quotient_Q_independence"])
        self.assertTrue(checks["simple_2_design"])
        self.assertTrue(checks["six_block_equations_under_notation_map"])
        self.assertTrue(checks["raw_binary_space_and_no_automorphism"])

    def test_spectrum_and_moments_are_reconstructed(self) -> None:
        spectral = self.results["spectral_reconstruction"]
        self.assertEqual(spectral["spectrum"], compare.EXPECTED_SPECTRUM)
        self.assertEqual(
            spectral["moments"],
            {"0": 70, "1": 0, "2": 630, "3": 336, "4": 13062},
        )
        self.assertEqual(spectral["edge_count"], 315)
        self.assertEqual(spectral["triangle_count"], 56)

    def test_four_cycles_and_determinant(self) -> None:
        spectral = self.results["spectral_reconstruction"]
        self.assertEqual(spectral["four_cycle_count"], 294)
        self.assertEqual(spectral["determinant"], "2^32*3^29")

    def test_triangle_census_closes(self) -> None:
        census = self.results["triangle_census_reconstruction"]
        self.assertEqual(census["D_edge_partition"], {"S": 42, "Q": 105, "O": 168})
        self.assertEqual(census["D_triangle_count"], 56)
        self.assertEqual(census["target_triangle_count"], 231)
        self.assertEqual(sum(census["target_triangle_partition"].values()), 231)

    def test_hostile_pg_design_is_exact(self) -> None:
        hostile = self.results["hostile_PG_3_2_reconstruction"]
        self.assertEqual(hostile["block_count"], 70)
        self.assertEqual(hostile["row_weight_set"], [3])
        self.assertEqual(hostile["column_weight_set"], [14])
        self.assertEqual(hostile["pair_intersection_set"], [2])
        self.assertEqual(
            hostile["B_sha256"],
            "dde3d4d8262a88e1de3078ae3fe3ef37087d2f3fed1ab251efe4c924292f81fb",
        )

    def test_hostile_pg_design_fails_fixed_label_coupling(self) -> None:
        hostile = self.results["hostile_PG_3_2_reconstruction"]
        self.assertEqual(hostile["FB_mismatch_count"], 135)
        self.assertFalse(hostile["checks"]["FB_equals_2J"])
        self.assertEqual(
            hostile["verdict"],
            "EXACT_ABSTRACT_DESIGN_BUT_NOT_FIXED_LABEL_COUPLING",
        )

    def test_graph_endpoint_scope_wall(self) -> None:
        scope = self.results["scope_review"]
        self.assertEqual(scope["report_graph_only_scope"], "PASS")
        self.assertEqual(scope["failed_routes_status_wall"], "PASS")
        self.assertFalse(scope["binary_solution_claimed"])
        self.assertFalse(scope["endpoint_solution_claimed"])

    def test_status_inflation_is_absent(self) -> None:
        checks = self.results["semantic_comparison"]["checks"]
        verdict = self.results["verdict"]
        self.assertTrue(checks["status_wall"])
        self.assertEqual(verdict["candidate_core_structural_claims"], "VERIFIED")
        self.assertEqual(verdict["binary_criterion_solution"], "UNKNOWN")
        self.assertEqual(verdict["rooted_endpoint"], "UNKNOWN")
        self.assertEqual(verdict["Conway_99"], "UNKNOWN")

    def test_no_material_discrepancy(self) -> None:
        verdict = self.results["verdict"]
        self.assertEqual(verdict["material_discrepancy"], "NONE_FOUND")
        self.assertEqual(
            verdict["candidate_manifest_and_results_consistency"],
            "VERIFIED",
        )

    def test_results_are_deterministic_lf_only_json(self) -> None:
        expected = compare.canonical_bytes(compare.build_results())
        parsed = json.loads(expected)
        self.assertEqual(parsed["schema_version"], 1)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "comparison-results.json"
            path.write_bytes(expected)
            observed = path.read_bytes()
        self.assertEqual(observed, expected)
        self.assertEqual(
            hashlib.sha256(observed).hexdigest(),
            hashlib.sha256(expected).hexdigest(),
        )
        self.assertNotIn(b"\r\n", observed)


if __name__ == "__main__":
    unittest.main()
