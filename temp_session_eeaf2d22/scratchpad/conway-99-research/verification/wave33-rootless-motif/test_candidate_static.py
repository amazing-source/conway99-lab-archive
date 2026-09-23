from __future__ import annotations

import copy
import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import candidate_static_check as check
import independent_check as independent


class RootlessMotifCandidateStaticTests(unittest.TestCase):
    def setUp(self) -> None:
        self.candidate = check.load_candidate_results()

    def test_full_static_comparison_verdict_and_status_wall(self) -> None:
        result = check.build_comparison()
        self.assertEqual(
            result["verdict"],
            "PASS_SCOPED_WITH_NONBLOCKING_WORDING_QUALIFIER",
        )
        obligations = result["obligations"]
        for key in (
            "global_realizability_of_local_tables",
            "partial_control_extendibility",
            "actual_global_motif_forcing",
            "actual_global_motif_avoidance",
            "rootless_endpoint",
            "n3_708",
            "Conway_99",
            "novelty",
        ):
            self.assertEqual(obligations[key], "UNKNOWN")

    def test_provenance_freezes_and_manifests_match(self) -> None:
        result = check.provenance_validation()
        self.assertEqual(result["candidate_freeze"]["entry_count"], 9)
        self.assertEqual(result["candidate_manifest"]["entry_count"], 8)
        self.assertEqual(result["candidate_input_freeze"]["entry_count"], 12)
        self.assertEqual(result["precomparison_manifest"]["entry_count"], 6)
        self.assertTrue(result["candidate_freeze"]["all_match"])
        self.assertTrue(result["precomparison_manifest"]["all_match"])

    def test_hostile_candidate_freeze_digest_is_active(self) -> None:
        with mock.patch.object(check, "CANDIDATE_FREEZE_SHA256", "0" * 64):
            with self.assertRaises(AssertionError):
                check.provenance_validation()

    def test_hostile_candidate_metadata_is_rejected(self) -> None:
        mutations = (
            ("scope", "Global construction."),
            ("uses_automorphism", True),
            ("constructs_global_graph_or_endpoint", True),
        )
        for field, value in mutations:
            with self.subTest(field=field):
                mutated = copy.deepcopy(self.candidate)
                mutated[field] = value
                with self.assertRaises(AssertionError):
                    check.metadata_comparison(mutated)
        mutated = copy.deepcopy(self.candidate)
        first_input = next(iter(mutated["inputs"]))
        mutated["inputs"][first_input] = "0" * 64
        with self.assertRaises(AssertionError):
            check.metadata_comparison(mutated)

    def test_hash_parser_rejects_duplicate_paths(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "duplicate.sha256"
            path.write_text(
                f"{'a' * 64}  same\n{'b' * 64} *same\n",
                encoding="utf-8",
            )
            with self.assertRaises(AssertionError):
                check.parse_hash_list(path)

    def test_algebra_matches_independent_reconstruction(self) -> None:
        result = check.algebra_comparison(self.candidate)
        self.assertEqual(result["basis_dimension"], 4)
        self.assertEqual(result["basis_independence_determinant"], 48510)
        self.assertTrue(result["Gamma_spectrum_match"])
        self.assertTrue(result["multiplication_identities_match"])

    def test_hostile_algebra_coefficient_is_rejected(self) -> None:
        mutated = copy.deepcopy(self.candidate)
        mutated["spectral_and_incidence_algebra"]["multiplication_identities"][
            "Gamma*C"
        ] = "-18*I+18*J-2*Gamma+C"
        with self.assertRaises(AssertionError):
            check.algebra_comparison(mutated)

    def test_candidate_tables_pass_scoped_feasibility(self) -> None:
        result = check.table_comparison(self.candidate)
        self.assertEqual(result["candidate_common_R3_counts"], [0, 1])
        self.assertTrue(result["null_trade_invisible_to_all_basis_pairs"])
        self.assertTrue(
            result["candidate_tables_differ_from_independent_controls"]
        )
        self.assertEqual(result["global_realizability"], "NOT_ESTABLISHED")

    def test_hostile_boolean_table_entry_is_rejected(self) -> None:
        mutated = copy.deepcopy(self.candidate)
        mutated["local_moment_controls"]["motif_zero"]["table"][0][0] = False
        with self.assertRaises(AssertionError):
            check.table_comparison(mutated)

    def test_hostile_feasible_table_with_changed_contraction_is_rejected(
        self,
    ) -> None:
        mutated = copy.deepcopy(self.candidate)
        table = mutated["local_moment_controls"]["motif_zero"]["table"]
        table[1][3] -= 1
        table[3][1] -= 1
        table[2][5] -= 1
        table[5][2] -= 1
        table[1][5] += 1
        table[5][1] += 1
        table[2][3] += 1
        table[3][2] += 1
        self.assertEqual([sum(row) for row in table], [1, 18, 22, 174, 6, 10])
        self.assertEqual(table, [list(row) for row in zip(*table)])
        self.assertTrue(all(entry >= 0 for row in table for entry in row))
        self.assertEqual((table[0][4], table[4][0], table[1][1]), (1, 1, 2))
        self.assertEqual(table[5][5], 0)
        with self.assertRaises(AssertionError):
            check.table_comparison(mutated)

    def test_hostile_table_metadata_is_rejected(self) -> None:
        mutated = copy.deepcopy(self.candidate)
        mutated["local_moment_controls"]["motif_one"][
            "common_R3_neighbours"
        ] = 0
        with self.assertRaises(AssertionError):
            check.table_comparison(mutated)

    def test_hostile_labelled_null_trade_is_rejected(self) -> None:
        mutated = copy.deepcopy(self.candidate)
        mutated["local_moment_controls"]["null_trade_one_minus_zero"][5][5] = 0
        with self.assertRaises(AssertionError):
            check.table_comparison(mutated)

    def test_transport_identity_and_literal_scope_qualifier(self) -> None:
        result = check.transport_comparison(self.candidate)
        self.assertTrue(result["identity_for_all_nonnegative_k"])
        self.assertFalse(result["R2_matrix_in_QGamma"])
        self.assertFalse(result["R3_matrix_in_QGamma"])
        self.assertEqual(result["literal_unqualified_phrase_status"], "TOO_BROAD")
        self.assertEqual(
            result["wording_objection"],
            "NONBLOCKING_IF_SCOPED_REPLACEMENT_IS_USED",
        )

    def test_hostile_transport_shift_is_rejected(self) -> None:
        mutated = copy.deepcopy(self.candidate)
        mutated["spectral_and_incidence_algebra"]["incidence_reduction"][
            "identity"
        ] = "N^T*A^k*N=(3I+Gamma)*(Gamma-3I)^k"
        with self.assertRaises(AssertionError):
            check.transport_comparison(mutated)

    def test_transport_limiting_text_is_an_active_gate(self) -> None:
        report = check.CANDIDATE_REPORT.read_text(encoding="utf-8")
        qualifier = (
            "Uncontracted three-leg incidence and full projector/Schur "
            "compatibility"
        )
        self.assertIn(qualifier, report)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "report.md"
            path.write_text(
                report.replace(qualifier, "Higher-order questions"),
                encoding="utf-8",
            )
            with mock.patch.object(check, "CANDIDATE_REPORT", path):
                with self.assertRaises(AssertionError):
                    check.transport_comparison(self.candidate)

    def test_board_is_derived_and_transversals_are_enumerated(self) -> None:
        derived = check.derive_r2_board()
        self.assertEqual(
            derived["counts"],
            [[1, 0, 1], [0, 1, 1], [1, 1, 2]],
        )
        self.assertEqual(derived["row_only"], [9, 9, 8])
        self.assertEqual(derived["column_only"], [9, 9, 8])
        self.assertEqual(derived["neither"], 33)
        self.assertEqual(len(derived["candidates"]), 4)
        result = check.board_and_partial_comparison(self.candidate)
        self.assertTrue(result["board_derived_from_lambda_mu"])
        self.assertTrue(result["transversals_independently_enumerated"])

    def test_hostile_base_relation_is_rejected(self) -> None:
        mutated = copy.deepcopy(self.candidate)
        mutated["actual_incidence_board"]["board"]["base_pair"][
            "relation"
        ] = "R0"
        with self.assertRaises(AssertionError):
            check.board_and_partial_comparison(mutated)

    def test_hostile_weighted_board_vertex_is_rejected(self) -> None:
        mutated = copy.deepcopy(self.candidate)
        mutated["actual_incidence_board"]["board"]["board_vertices"][0][
            "u_index"
        ] = 1
        with self.assertRaises(AssertionError):
            check.board_and_partial_comparison(mutated)

    def test_hostile_transversal_enumeration_is_rejected(self) -> None:
        mutated = copy.deepcopy(self.candidate)
        candidates = mutated["actual_incidence_board"]["board"][
            "transversal_candidates"
        ]
        candidates[0] = ["b00_0", "b12_0", "b20_0"]
        with self.assertRaises(AssertionError):
            check.board_and_partial_comparison(mutated)

    def test_hostile_partial_control_metadata_is_rejected(self) -> None:
        mutations = (
            ("vertex_count", 98),
            ("mode", "global_graph"),
            ("closed_transversal_count", 9),
            ("all_base_pair_lambda_mu_counts_exact", False),
            ("all_present_pair_common_neighbour_caps_pass", False),
            ("scope", "Complete SRG extension."),
        )
        for field, value in mutations:
            with self.subTest(field=field):
                mutated = copy.deepcopy(self.candidate)
                mutated["actual_incidence_board"]["partial_controls"][
                    "motif_free"
                ][field] = value
                with self.assertRaises(AssertionError):
                    check.board_and_partial_comparison(mutated)

    def test_partial_control_limiting_text_is_an_active_gate(self) -> None:
        report = check.CANDIDATE_REPORT.read_text(encoding="utf-8")
        qualifier = (
            "They are not graph constructions or extension\ncertificates."
        )
        self.assertIn(qualifier, report)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "report.md"
            path.write_text(
                report.replace(qualifier, "They are complete graphs."),
                encoding="utf-8",
            )
            with mock.patch.object(check, "CANDIDATE_REPORT", path):
                with self.assertRaises(AssertionError):
                    check.board_and_partial_comparison(self.candidate)

    def test_mixed_trace_factor_two_has_independent_witness(self) -> None:
        self.assertEqual(
            check.independent_trace_factor(),
            {
                "unordered_motifs": 1,
                "ordered_R2_orientations": 2,
                "trace": 2,
            },
        )
        result = check.mixed_trace_and_status(self.candidate)
        self.assertEqual(result["unordered_motif_multiplier"], 2)

    def test_hostile_trace_factor_is_rejected(self) -> None:
        mutated = copy.deepcopy(self.candidate)
        mutated["mixed_trace"]["unordered_motif_multiplier"] = 1
        with self.assertRaises(AssertionError):
            check.mixed_trace_and_status(mutated)

    def test_hostile_status_promotion_and_extra_status_are_rejected(self) -> None:
        for mutation in ("promotion", "extra"):
            with self.subTest(mutation=mutation):
                mutated = copy.deepcopy(self.candidate)
                if mutation == "promotion":
                    mutated["status"]["Conway_99"] = "VERIFIED"
                else:
                    mutated["status"]["global_graph_exists"] = "VERIFIED"
                with self.assertRaises(AssertionError):
                    check.mixed_trace_and_status(mutated)

    def test_hostile_empty_blocking_objection_is_rejected(self) -> None:
        mutated = copy.deepcopy(self.candidate)
        mutated["strongest_self_objection"]["objection"] = ""
        with self.assertRaises(AssertionError):
            check.mixed_trace_and_status(mutated)

    def test_candidate_code_is_read_statically_and_never_imported(self) -> None:
        before = set(sys.modules)
        audit = check.static_source_audit()
        after = set(sys.modules)
        self.assertNotIn("exact_check", after - before)
        self.assertFalse(audit["candidate_source_imported"])
        self.assertFalse(audit["candidate_source_executed"])
        self.assertTrue(audit["candidate_test_file_imports_discovery_code"])

    def test_comparison_json_is_deterministic_lf_only(self) -> None:
        first = independent.canonical_bytes(check.build_comparison())
        second = independent.canonical_bytes(check.build_comparison())
        self.assertEqual(first, second)
        artifact = Path(check.__file__).parent / "comparison-results.json"
        self.assertEqual(artifact.read_bytes(), first)
        self.assertNotIn(b"\r\n", first)
        self.assertEqual(
            hashlib.sha256(first).hexdigest(),
            hashlib.sha256(second).hexdigest(),
        )
        parsed = json.loads(first)
        self.assertFalse(parsed["candidate_code_imported_or_executed"])


if __name__ == "__main__":
    unittest.main()
