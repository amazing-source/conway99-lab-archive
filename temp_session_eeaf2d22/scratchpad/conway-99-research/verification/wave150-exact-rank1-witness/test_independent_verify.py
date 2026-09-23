"""Focused and hostile checks for the Wave150 independent verifier."""

from __future__ import annotations

import importlib.util
import json
import sys
import unittest
from fractions import Fraction
from pathlib import Path


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "wave150_independent_verify", HERE / "independent_verify.py"
)
assert SPEC is not None and SPEC.loader is not None
VERIFY = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = VERIFY
SPEC.loader.exec_module(VERIFY)
RESULT = json.loads(
    (HERE / "verification-results.json").read_text(encoding="utf-8")
)


class Wave150IndependentTests(unittest.TestCase):
    def test_sealed_inputs_and_separation(self) -> None:
        chronology = RESULT["chronology"]
        manifest = chronology["sealed_discovery_manifest"]
        self.assertEqual(manifest["entry_count"], 30)
        self.assertTrue(manifest["manifest_pass"])
        self.assertTrue(manifest["entries_pass"])
        self.assertFalse(chronology["discovery_code_imported_or_executed"])
        self.assertEqual(
            RESULT["witness"]["sha256"],
            VERIFY.EXPECTED_WITNESS_SHA256,
        )

    def test_complete_reconstruction_dimensions(self) -> None:
        self.assertEqual(RESULT["wave44"]["rows"], 170)
        self.assertEqual(
            RESULT["wave147"]["full_matrix_records_reconstructed"], 2414
        )
        self.assertEqual(
            RESULT["wave147"]["nonzero_upper_entries_reconstructed"], 272054
        )
        self.assertEqual(RESULT["wave148"]["total_rows"], 5384)
        replay = RESULT["full_equation_replay"]
        self.assertEqual(replay["equations_before_trivial_removal"], 11632)
        self.assertEqual(replay["nontrivial_equations"], 10310)
        self.assertEqual(replay["restricted_nontrivial_equations"], 10259)
        self.assertTrue(replay["all_10310_rows_pass_exactly"])

    def test_rational_shape_and_totals(self) -> None:
        witness = RESULT["witness"]
        self.assertEqual(witness["x7_support"], 204)
        self.assertEqual(witness["x8_support"], 874)
        self.assertEqual(
            witness["x8_denominator_distribution"],
            {"1": 865, "2": 5, "4": 4},
        )
        self.assertEqual(witness["x7_total"], 14887031544)
        self.assertEqual(witness["x8_total"], "171200862756")
        self.assertTrue(witness["all_counts_nonnegative"])

    def test_both_centered_blocks(self) -> None:
        centered = RESULT["centered_covariance"]
        self.assertEqual(centered["ordered_edge"]["size"], 66)
        self.assertEqual(centered["ordered_edge"]["upper_entries"], 2211)
        self.assertEqual(centered["ordered_nonedge"]["size"], 87)
        self.assertEqual(
            centered["ordered_nonedge"]["upper_entries"], 3828
        )
        for block in centered.values():
            self.assertTrue(block["all_centered_entries_exactly_zero"])
            self.assertEqual(
                block["first_moment_sum"],
                block["expected_first_moment_sum"],
            )
            self.assertEqual(
                block["moment_sum"], block["expected_moment_sum"]
            )

    def test_modular_selection(self) -> None:
        modular = RESULT["modular_selection"]
        self.assertEqual(modular["modulus"], 1000003)
        self.assertEqual(modular["variables"], 874)
        self.assertEqual(modular["rank"], 874)
        self.assertEqual(modular["rows_scanned_to_full_rank"], 1931)
        self.assertEqual(
            modular["stored_874_by_874_subsystem_rank"], 874
        )
        self.assertTrue(modular["stored_selected_indices_exact_match"])
        self.assertTrue(modular["stored_selected_labels_exact_match"])

    def test_false_infeasibility_chronology(self) -> None:
        chronology = RESULT["chronology"]["false_infeasibility_retained"]
        self.assertEqual(
            chronology["initial_bound_encoding_status"], "infeasible"
        )
        self.assertEqual(
            chronology["explicit_inequality_encoding_status"], "optimal"
        )
        self.assertTrue(
            chronology[
                "exact_witness_refutes_infeasibility_for_the_exact_system"
            ]
        )
        self.assertFalse(chronology["solver_exit_code_used_as_certificate"])

    def test_hostile_rational_encoding(self) -> None:
        self.assertEqual(VERIFY.parse_fraction("7/4", "good"), Fraction(7, 4))
        for bad in ("2/2", "0/2", "1/-2", " 1/2"):
            with self.assertRaises(AssertionError):
                VERIFY.parse_fraction(bad, "hostile")

    def test_hostile_equation_mutation(self) -> None:
        x8 = {10: Fraction(3, 2), 20: Fraction(5)}
        row = {
            "coefficients": {10: 2, 20: 1},
            "rhs": 8,
        }
        self.assertEqual(VERIFY.evaluate_equation(row, x8), 0)
        row["coefficients"][10] += 1
        self.assertEqual(VERIFY.evaluate_equation(row, x8), Fraction(3, 2))

    def test_hostile_modular_dependency(self) -> None:
        support = (10, 20)
        independent = [
            {"label": "a", "coefficients": {10: 1}},
            {"label": "b", "coefficients": {20: 1}},
        ]
        rank, scanned, _, _ = VERIFY.modular_rank(
            independent, support, 1000003
        )
        self.assertEqual((rank, scanned), (2, 2))
        dependent = [
            independent[0],
            {"label": "copy", "coefficients": {10: 2}},
        ]
        rank, scanned, _, _ = VERIFY.modular_rank(
            dependent, support, 1000003
        )
        self.assertEqual((rank, scanned), (1, 2))

    def test_scope_wall(self) -> None:
        self.assertEqual(RESULT["verdict"]["overall"], "PASS_WITH_SCOPE")
        self.assertEqual(
            RESULT["verdict"]["finite_relaxation_at_n3_4158"],
            "EXACT_RATIONAL_FEASIBLE",
        )
        wall = RESULT["status_wall"]
        self.assertFalse(wall["exact_count_vector_is_a_graph"])
        self.assertEqual(
            wall["endpoint_n3_4158_graph_existence"], "UNKNOWN"
        )
        self.assertEqual(wall["Conway_99"], "UNKNOWN")


if __name__ == "__main__":
    unittest.main()
