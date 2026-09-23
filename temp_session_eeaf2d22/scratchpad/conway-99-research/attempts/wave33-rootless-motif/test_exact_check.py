#!/usr/bin/env python3
"""Hostile deterministic tests for the Wave 33 rootless-motif checker."""

from __future__ import annotations

import copy
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

import exact_check


class Wave33RootlessMotifTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = exact_check.build_result()

    def test_frozen_inputs_match(self) -> None:
        self.assertEqual(
            self.result["inputs"],
            exact_check.FROZEN_INPUTS,
        )

    def test_spectral_multiplication_table(self) -> None:
        algebra = self.result["spectral_and_incidence_algebra"]
        self.assertEqual(algebra["C_spectrum"], [216, -4, -18, 6])
        self.assertEqual(algebra["M_spectrum"], [0, 0, 21, 0])
        self.assertEqual(
            algebra["multiplication_identities"],
            {
                "Gamma^2": "18*I+5*Gamma+C",
                "Gamma*C": "-18*I+18*J-2*Gamma-C",
                "C^2": "72*I+216*J-16*Gamma-14*C",
            },
        )

    def test_two_leg_incidence_reduces_to_gamma_algebra(self) -> None:
        reduction = self.result[
            "spectral_and_incidence_algebra"
        ]["incidence_reduction"]
        self.assertEqual(
            reduction["identity"],
            "N^T*A^k*N=(3I+Gamma)*(Gamma-4I)^k",
        )
        for values in reduction["spectral_values"].values():
            self.assertEqual(values[-1], 0)
        self.assertIn("uncontracted vertex labels", reduction["does_not_cover"])

    def test_both_local_tables_are_nonnegative_with_q2_margins(self) -> None:
        controls = self.result["local_moment_controls"]
        expected = {"D": 1, "G": 18, "R0": 22, "R1": 174, "R2": 6, "R3": 10}
        for name in ("motif_zero", "motif_one"):
            control = controls[name]
            self.assertEqual(control["row_and_column_margins"], expected)
            self.assertTrue(
                all(value >= 0 for row in control["table"] for value in row)
            )
            self.assertEqual(control["q_endpoint_values"], [2, 2])

    def test_all_gamma_algebra_contractions_match(self) -> None:
        controls = self.result["local_moment_controls"]
        expected = [list(row) for row in exact_check.EXPECTED_R2_CONTRACTION]
        self.assertEqual(
            controls["motif_zero"]["basis_contraction_matrix"], expected
        )
        self.assertEqual(
            controls["motif_one"]["basis_contraction_matrix"], expected
        )

    def test_projector_entry_is_active(self) -> None:
        controls = self.result["local_moment_controls"]
        self.assertEqual(
            controls["motif_zero"]["projector_contraction_M_squared"], -21
        )
        self.assertEqual(
            controls["motif_one"]["projector_contraction_M_squared"], -21
        )
        mutation = copy.deepcopy(
            controls["motif_zero"]["table"]
        )
        mutation[5][5] += 1
        self.assertNotEqual(
            exact_check.contraction_matrix(mutation),
            [list(row) for row in exact_check.EXPECTED_R2_CONTRACTION],
        )

    def test_null_trade_is_invisible_but_changes_motif(self) -> None:
        controls = self.result["local_moment_controls"]
        delta = controls["null_trade_one_minus_zero"]
        self.assertEqual(exact_check.row_sums(delta), [0] * 6)
        self.assertEqual(exact_check.column_sums(delta), [0] * 6)
        self.assertEqual(
            exact_check.contraction_matrix(delta),
            [[0] * 4 for _ in range(4)],
        )
        self.assertEqual(delta[5][5], 1)

    def test_mixed_trace_normalization(self) -> None:
        trace = self.result["mixed_trace"]
        self.assertEqual(trace["unordered_motif_multiplier"], 2)
        self.assertEqual(trace["rootless_required_value"], 0)
        self.assertEqual(
            trace["actual_incidence_forces_positive_value"], "UNKNOWN"
        )

    def test_actual_incidence_board_census(self) -> None:
        board = self.result["actual_incidence_board"]["board"]
        self.assertEqual(
            board["both_side_common_neighbour_counts"],
            [[1, 0, 1], [0, 1, 1], [1, 1, 2]],
        )
        self.assertEqual(board["board_size"], 8)
        self.assertEqual(board["row_only_counts"], [9, 9, 8])
        self.assertEqual(board["column_only_counts"], [9, 9, 8])
        self.assertEqual(board["neither_side_count"], 33)
        self.assertEqual(board["outside_vertex_total"], 93)

    def test_exactly_four_transversal_candidates(self) -> None:
        board = self.result["actual_incidence_board"]["board"]
        self.assertEqual(board["transversal_candidate_count_per_R2_pair"], 4)
        self.assertEqual(len(board["transversal_candidates"]), 4)
        self.assertEqual(board["pair_indexed_candidates_at_n3_708"], 2832)
        for triple in board["transversal_candidates"]:
            metadata = {
                item["name"]: item
                for item in board["board_vertices"]
            }
            self.assertEqual(
                {metadata[name]["t_index"] for name in triple},
                {0, 1, 2},
            )
            self.assertEqual(
                {metadata[name]["u_index"] for name in triple},
                {0, 1, 2},
            )

    def test_partial_controls_are_parameter_cap_compatible(self) -> None:
        partial = self.result["actual_incidence_board"]["partial_controls"]
        for control in partial.values():
            self.assertEqual(control["vertex_count"], 99)
            self.assertEqual(
                control["base_vertex_degrees"],
                {"t0": 14, "t1": 14, "t2": 14,
                 "u0": 14, "u1": 14, "u2": 14},
            )
            self.assertTrue(
                control["all_present_pair_common_neighbour_caps_pass"]
            )
            self.assertTrue(control["all_base_pair_lambda_mu_counts_exact"])

    def test_partial_controls_separate_closure_without_claiming_completion(self) -> None:
        partial = self.result["actual_incidence_board"]["partial_controls"]
        self.assertEqual(partial["motif_free"]["closed_transversal_count"], 0)
        self.assertEqual(partial["motif_one"]["closed_transversal_count"], 1)
        for control in partial.values():
            self.assertIn("not an SRG extension", control["scope"])
            self.assertIn("remain unspecified", control["scope"])

    def test_status_wall_and_strongest_objection(self) -> None:
        status = self.result["status"]
        self.assertEqual(status["Q_Gamma_two_leg_local_blindness"], "DERIVED")
        self.assertEqual(
            status["fully_contracted_two_leg_incidence_local_blindness"],
            "DERIVED",
        )
        for key in (
            "actual_incidence_forces_positive_mixed_trace",
            "rootless_indecomposable_endpoint",
            "n3_708",
            "Conway_99",
            "novelty",
        ):
            self.assertEqual(status[key], "UNKNOWN")
        objection = self.result["strongest_self_objection"]
        self.assertEqual(objection["disposition"], "VALID_AND_BLOCKING")
        self.assertIn("not prove", objection["objection"])

    def test_canonical_json_is_deterministic_and_lf_only(self) -> None:
        first = exact_check.render(self.result)
        second = exact_check.render(exact_check.build_result())
        self.assertEqual(first, second)
        self.assertTrue(first.endswith("\n"))
        self.assertNotIn("\r", first)
        parsed = json.loads(first)
        self.assertEqual(parsed, self.result)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "result.json"
            exact_check.write_json(path, self.result)
            payload = path.read_bytes()
        self.assertEqual(payload, first.encode("utf-8"))
        self.assertEqual(
            hashlib.sha256(payload).hexdigest(),
            hashlib.sha256(first.encode("utf-8")).hexdigest(),
        )


if __name__ == "__main__":
    unittest.main()
