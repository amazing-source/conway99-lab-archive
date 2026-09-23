"""Post-handoff hostile tests for the independent Wave148 verifier."""

from __future__ import annotations

import copy
import json
import sys
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import independent_verify as verify  # noqa: E402


class IndependentWave148Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.expected, _ = verify.expected_row_payload()
        cls.result = json.loads(
            (HERE / "verification-results.json").read_text(encoding="utf-8")
        )

    def test_chronology_and_manifests(self) -> None:
        chronology = self.result["chronology"]
        self.assertEqual(
            chronology["preparation_manifest"]["manifest_sha256"],
            verify.EXPECTED_PREPARATION_MANIFEST_SHA256,
        )
        self.assertEqual(
            chronology["discovery_manifest"]["manifest_sha256"],
            verify.EXPECTED_DISCOVERY_MANIFEST_SHA256,
        )
        self.assertTrue(chronology["preparation_preceded_discovery_handoff"])
        self.assertFalse(chronology["discovery_code_imported_or_executed"])

    def test_complete_exact_comparison(self) -> None:
        comparison = self.result["complete_row_comparison"]
        self.assertEqual(comparison["vertex_rows"], 944)
        self.assertEqual(comparison["ordered_pair_rows"], 4440)
        self.assertEqual(comparison["vertex_nonzero_terms"], 10872)
        self.assertEqual(comparison["pair_nonzero_terms"], 17782)
        self.assertEqual(comparison["zero_capacity_pair_rows"], 893)
        self.assertEqual(comparison["zero_rhs_pair_rows"], 893)
        self.assertTrue(comparison["every_scalar_and_coefficient_exact_match"])

    def test_artifact_integrity_and_semantic_normalization(self) -> None:
        artifact = self.result["artifact"]
        self.assertEqual(
            artifact["gzip_sha256"], verify.EXPECTED_DISCOVERY_GZIP_SHA256
        )
        self.assertEqual(
            artifact["canonical_sha256"],
            verify.EXPECTED_DISCOVERY_PAYLOAD_SHA256,
        )
        self.assertFalse(artifact["clean_room_raw_layout_exact_match"])
        self.assertTrue(
            artifact["clean_room_semantic_normalized_exact_match"]
        )
        self.assertEqual(
            artifact["clean_room_semantic_normalized_sha256"],
            artifact["discovery_semantic_normalized_sha256"],
        )

    def test_hostile_vertex_coefficient_mutation(self) -> None:
        altered = copy.deepcopy(self.expected)
        altered["vertex_rows"][0]["terms_order8_mask_coefficient"][0][1] += 1
        self.assertIn(
            "vertex_rows",
            verify.first_payload_difference(self.expected, altered),
        )

    def test_hostile_pair_root_order_mutation(self) -> None:
        index = next(
            index
            for index, row in enumerate(self.expected["ordered_pair_rows"])
            if verify.clean.canonical_rooted(
                row["rooted_key"], 7, (1, 0)
            )
            != row["rooted_key"]
        )
        altered = copy.deepcopy(self.expected)
        row = altered["ordered_pair_rows"][index]
        row["rooted_key"] = verify.clean.canonical_rooted(
            row["rooted_key"], 7, (1, 0)
        )
        self.assertIn(
            "ordered_pair_rows",
            verify.first_payload_difference(self.expected, altered),
        )

    def test_hostile_multiplicity_and_residual_mutations(self) -> None:
        altered = copy.deepcopy(self.expected)
        altered["vertex_rows"][10]["orbit_multiplicity"] += 1
        self.assertIn(
            "vertex_rows",
            verify.first_payload_difference(self.expected, altered),
        )
        altered = copy.deepcopy(self.expected)
        altered["ordered_pair_rows"][100][
            "outside_common_neighbor_count"
        ] += 1
        self.assertIn(
            "ordered_pair_rows",
            verify.first_payload_difference(self.expected, altered),
        )

    def test_zero_capacity_and_controls(self) -> None:
        comparison = self.result["complete_row_comparison"]
        self.assertTrue(comparison["zero_capacity_support_exact_match"])
        self.assertTrue(comparison["semantic_row_key_sets_exact_match"])
        for sequence in comparison["discovery_sequence_checks"].values():
            self.assertTrue(sequence["row_ids_sequential"])
            self.assertTrue(sequence["semantic_keys_unique"])
            self.assertTrue(sequence["source_then_rooted_key_order"])
        controls = self.result["independent_controls"]
        self.assertEqual(controls["column_classes_checked"], 916)
        self.assertTrue(controls["all_vertex_column_identities_pass"])
        self.assertTrue(controls["all_pair_column_identities_pass"])
        self.assertTrue(controls["rook"]["all_rows_pass"])
        micro = controls["micro_controls"]
        self.assertEqual(
            micro["degree_empty7_to_one_edge8"]["coefficient"], 2
        )
        self.assertEqual(
            micro["nonedge_CN_empty7_to_path8"]["coefficient"], 2
        )
        self.assertEqual(
            micro["edge_CN_one_edge7_to_triangle8"]["coefficient"], 6
        )

    def test_scope_wall(self) -> None:
        self.assertEqual(self.result["verdict"]["overall"], "PASS_WITH_SCOPE")
        self.assertEqual(
            self.result["status_wall"]["combined_Wave147_148_SDP"],
            "NOT_RUN",
        )
        self.assertEqual(
            self.result["status_wall"]["strict_n3_upper_bound"], "UNKNOWN"
        )
        self.assertEqual(self.result["status_wall"]["Conway_99"], "UNKNOWN")


if __name__ == "__main__":
    unittest.main()
