from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from pathlib import Path

import independent_check as check


class IndependentIndecomposableTests(unittest.TestCase):
    def test_frozen_inputs(self) -> None:
        self.assertEqual(check.verify_input_freeze(), check.read_input_freeze())

    def test_candidate_manifests_without_executing_candidate(self) -> None:
        self.assertEqual(
            check.candidate_manifest_validation(),
            {
                "artifact_manifest_entries": 7,
                "input_freeze_entries": 5,
                "all_hashes_match": True,
            },
        )

    def test_primitive_rows_generate(self) -> None:
        result = check.primitive_row_generation()
        self.assertEqual(result["primitive_index"], 1)
        self.assertEqual(result["nonprimitive_index"], 2)
        self.assertTrue(result["primitive_rows_generate"])

    def test_connectivity_decomposition_controls(self) -> None:
        result = check.connectivity_and_decomposition()
        self.assertEqual(result["decomposable_components"], [[0], [1]])
        self.assertEqual(result["indecomposable_components"], [[0, 1]])
        self.assertEqual(result["indecomposable_rank_two_determinant"], 15)

    def test_minimum_floor_is_active(self) -> None:
        result = check.connectivity_and_decomposition()
        self.assertEqual(result["dropped_minimum_mixed_row_norm"], 4)

    def test_wave31_actual_incidence_implication_is_scoped(self) -> None:
        result = check.connectivity_and_decomposition()
        self.assertIn(
            "actual rootless endpoint",
            result["actual_incidence_consequence"],
        )
        self.assertIn("Wave31", result["actual_incidence_consequence"])

    def test_unique_switched_root_motif(self) -> None:
        result = check.motif_census()
        self.assertEqual(result["raw_count"], 3)
        self.assertEqual(result["switching_class_count"], 1)
        self.assertEqual(result["canonical_determinant"], 20)
        self.assertEqual(result["canonical_all_ones_norm"], 2)

    def test_positive_one_sign_mutation_survives_root_screen(self) -> None:
        result = check.motif_census()
        self.assertNotIn(2, result["positive_one_mutation_norms"])

    def test_trace_factor_is_exactly_two(self) -> None:
        result = check.trace_factor_two()
        self.assertEqual(result["one_motif_trace"], 2)
        self.assertEqual(result["two_motif_trace"], 4)
        self.assertEqual(result["factor"], 2)

    def test_endpoint_ordered_pair_counts(self) -> None:
        result = check.endpoint_pair_counts()
        self.assertEqual(
            result["ordered"],
            {
                "plus_1": 5092,
                "minus_1": 1416,
                "minus_2": 2300,
                "zero": 44322,
            },
        )
        self.assertEqual(result["ordered_total"], 231 * 230)

    def test_endpoint_unordered_pair_counts(self) -> None:
        result = check.endpoint_pair_counts()
        self.assertEqual(
            result["unordered"],
            {
                "plus_1": 2546,
                "minus_1": 708,
                "minus_2": 1150,
                "zero": 22161,
            },
        )
        self.assertEqual(result["unordered_total"], 231 * 230 // 2)

    def test_all_eight_finite_field_rank_rows(self) -> None:
        rows = check.finite_field_rank_table()
        observed = [
            (
                row["h"],
                row["rank_S_mod_3"],
                row["rank_G_mod_3"],
                row["rank_S_mod_7"],
                row["rank_G_mod_7"],
            )
            for row in rows
        ]
        self.assertEqual(
            observed,
            [
                (9, 42, 2, 44, 0),
                (21, 43, 1, 43, 1),
                (49, 44, 0, 42, 2),
                (81, 40, 4, 44, 0),
                (189, 41, 3, 43, 1),
                (441, 42, 2, 42, 2),
                (729, 38, 6, 44, 0),
                (1029, 43, 1, 41, 3),
            ],
        )

    def test_rank_complements_and_hulls(self) -> None:
        for row in check.finite_field_rank_table():
            self.assertEqual(
                row["rank_S_mod_3"] + row["rank_G_mod_3"],
                44,
            )
            self.assertEqual(row["rank_M_mod_3"], row["rank_S_mod_3"])
            self.assertEqual(
                row["rank_S_mod_7"] + row["rank_G_mod_7"],
                44,
            )
            self.assertEqual(row["rank_M_mod_7"], row["rank_S_mod_7"])
            self.assertEqual(
                row["hull_dimension_mod_3"],
                44 - row["rank_G_mod_3"],
            )
            self.assertEqual(
                row["hull_dimension_mod_7"],
                44 - row["rank_G_mod_7"],
            )

    def test_universal_self_orthogonality_is_false(self) -> None:
        controls = check.finite_field_hostile_controls()
        self.assertEqual(controls["F3_nonself_gram"], [[1]])
        self.assertEqual(controls["F7_nonself_gram"], [[1]])
        rows = check.finite_field_rank_table()
        self.assertTrue(any(not row["code_self_orthogonal_mod_3"] for row in rows))
        self.assertTrue(any(not row["code_self_orthogonal_mod_7"] for row in rows))

    def test_full_rank_X_can_have_singular_gram(self) -> None:
        controls = check.finite_field_hostile_controls()
        self.assertEqual(controls["F3_full_rank_X_gram_rank"], [1, 0])
        self.assertEqual(controls["F7_full_rank_X_gram_rank"], [1, 0])

    def test_231_row_binary_hostile_control(self) -> None:
        result = check.binary_hostile_control()
        self.assertEqual(result["row_count"], 231)
        self.assertEqual(result["rank_X"], 44)
        self.assertEqual(result["projector_rank"], 44)
        self.assertTrue(result["projector_idempotent"])
        self.assertTrue(result["projector_alternating"])
        self.assertTrue(result["projector_kills_one"])
        self.assertTrue(result["all_rows_quadratically_singular"])
        self.assertTrue(result["row_sum_zero"])
        self.assertTrue(result["nonorthogonality_connected"])
        self.assertEqual(result["odd_pair_count"], 806)

    def test_pair_counts_and_connectivity_do_not_force_motif(self) -> None:
        result = check.pair_count_hostile_control()
        self.assertTrue(result["connected"])
        self.assertEqual(
            result["unordered_counts"],
            check.endpoint_pair_counts()["unordered"],
        )
        self.assertEqual(result["motif_count"], 0)
        self.assertEqual(result["motif_trace"], 0)

    def test_status_wall(self) -> None:
        results = check.build_results()
        self.assertEqual(
            results["claim_label"],
            "VERIFIED_SCOPED_WITH_NONBLOCKING_COVERAGE_GAPS",
        )
        status = results["status"]
        self.assertEqual(
            status,
            {
                "motif_forcing": "UNKNOWN",
                "indecomposable_endpoint": "UNKNOWN",
                "n3_708": "UNKNOWN",
                "Conway_99": "UNKNOWN",
                "novelty": "UNKNOWN",
            },
        )

    def test_deterministic_lf_json(self) -> None:
        encoded = check.canonical_bytes(check.build_results())
        parsed = json.loads(encoded)
        self.assertEqual(parsed["schema_version"], 1)
        self.assertNotIn(b"\r\n", encoded)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "result.json"
            path.write_bytes(encoded)
            replay = path.read_bytes()
        self.assertEqual(replay, encoded)
        self.assertEqual(
            hashlib.sha256(replay).hexdigest(),
            hashlib.sha256(encoded).hexdigest(),
        )


if __name__ == "__main__":
    unittest.main()
