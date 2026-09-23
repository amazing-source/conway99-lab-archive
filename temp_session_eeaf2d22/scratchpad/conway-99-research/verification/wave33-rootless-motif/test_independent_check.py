from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from fractions import Fraction
from pathlib import Path

import independent_check as check


class RootlessMotifIndependentTests(unittest.TestCase):
    def test_public_input_freeze(self) -> None:
        self.assertEqual(check.verify_frozen_inputs(), check.FROZEN_INPUTS)

    def test_gamma_basis_and_minimal_polynomial(self) -> None:
        result = check.gamma_multiplication_table()
        self.assertEqual(result["dimension"], 4)
        self.assertEqual(result["basis"], ["I", "J", "Gamma", "C"])
        self.assertEqual(result["basis_evaluation_determinant"], 48510)
        self.assertEqual(
            result["minimal_polynomial_expanded"],
            "x^4-22x^3+51x^2+378x",
        )

    def test_gamma_multiplication_table(self) -> None:
        products = check.gamma_multiplication_table()["multiplication"]
        self.assertEqual(products["Gamma*Gamma"], [18, 0, 5, 1])
        self.assertEqual(products["Gamma*C"], [-18, 18, -2, -1])
        self.assertEqual(products["C*C"], [72, 216, -16, -14])
        self.assertEqual(products["J*C"], [0, 216, 0, 0])

    def test_hostile_wrong_C_coefficient_is_active(self) -> None:
        result = check.hostile_wrong_C_coefficient()
        self.assertEqual(result["target_intersecting_entry"], 0)
        self.assertEqual(result["hostile_intersecting_entry"], 1)
        self.assertFalse(result["hostile_still_represents_cross_edge_count"])

    def test_q_two_margins(self) -> None:
        self.assertEqual(check.margins_for_q(2), [1, 18, 22, 174, 6, 10])
        self.assertEqual(sum(check.margins_for_q(2)), 231)
        self.assertNotEqual(check.margins_for_q(3), check.margins_for_q(2))

    def test_local_tables_nonnegative_symmetric_and_fixed(self) -> None:
        zero, one = check.local_tables()
        for table in (zero, one):
            result = check.validate_local_table(table)
            self.assertEqual(result["margins"], [1, 18, 22, 174, 6, 10])
            self.assertEqual(
                result["fixed_cells"],
                {"D_R2": 1, "R2_D": 1, "Gamma_Gamma": 2},
            )

    def test_tables_have_identical_QGamma_contractions(self) -> None:
        result = check.algebraic_local_nonforcing()
        expected = [
            [0, 1, 0, 2],
            [1, 231, 18, 216],
            [0, 18, 2, 16],
            [2, 216, 16, 188],
        ]
        self.assertEqual(result["shared_QGamma_contractions"], expected)
        self.assertEqual(result["common_R3_counts"], [0, 1])
        self.assertEqual(result["trace_contribution_for_unordered_R2_pair"], [0, 2])

    def test_table_switch_is_invisible_to_full_basis(self) -> None:
        result = check.algebraic_local_nonforcing()
        switch = result["switch"]
        self.assertEqual(result["switch_row_sums"], [0] * 6)
        vectors = check.entry_vectors()
        for left in check.BASIS:
            for right in check.BASIS:
                self.assertEqual(
                    check.bilinear_contraction(
                        vectors[left],
                        switch,
                        vectors[right],
                    ),
                    0,
                )
        self.assertEqual(switch[5][5], 1)

    def test_table_pair_existence_scope_is_formal(self) -> None:
        scope = check.algebraic_local_nonforcing()["pair_scope"]
        self.assertTrue(scope["formal_only"])
        self.assertEqual(scope["global_existence_of_such_pair"], "NOT_PROVED")
        self.assertEqual(scope["relation"], "R2")

    def test_table_q_mutation_is_rejected(self) -> None:
        table, _ = check.local_tables()
        with self.assertRaises(AssertionError):
            mutated = [row[:] for row in table]
            # Move one unit without preserving the q=2 margin.
            mutated[2][2] += 1
            check.validate_local_table(mutated)

    def test_incidence_transport_first_rows(self) -> None:
        rows = check.incidence_transport()["first_nine_exact_reductions"]
        self.assertEqual(
            rows[0]["basis_coefficients_I_J_Gamma_C"],
            [3, 0, 1, 0],
        )
        self.assertEqual(
            rows[1]["basis_coefficients_I_J_Gamma_C"],
            [6, 0, 4, 1],
        )
        self.assertEqual(
            rows[2]["basis_coefficients_I_J_Gamma_C"],
            [30, 18, 8, -1],
        )

    def test_incidence_transport_exact_for_nine_powers(self) -> None:
        rows = check.incidence_transport()["first_nine_exact_reductions"]
        for row in rows:
            exponent = row["k"]
            coefficients = row["reduced_polynomial_coefficients_ascending"]
            for eigenvalue in (18, 7, 0, -3):
                observed = sum(
                    coefficient * eigenvalue ** degree
                    for degree, coefficient in enumerate(coefficients)
                )
                expected = (eigenvalue + 3) * (eigenvalue - 4) ** exponent
                self.assertEqual(observed, expected)

    def test_transport_shift_minus_four_is_active(self) -> None:
        hostile = check.incidence_transport()["hostile_shift_minus_3"]
        self.assertEqual(hostile["correct_shift"], -4)
        self.assertEqual(hostile["hostile_shift"], -3)
        self.assertFalse(hostile["passes"])

    def test_individual_relation_matrices_are_not_in_fused_algebra(self) -> None:
        result = check.fused_algebra_scope()
        self.assertEqual(
            result["individual_relation_indicators_affine"],
            {"R0": False, "R1": False, "R2": False, "R3": False},
        )
        self.assertFalse(result["R3_matrix_in_QGamma"])
        self.assertFalse(result["common_R3_determined_by_QGamma"])

    def test_exact_R2_multiplicity_board(self) -> None:
        result = check.actual_incidence_board()
        self.assertEqual(
            result["multiplicity_board"],
            [[1, 0, 1], [0, 1, 1], [1, 1, 2]],
        )
        self.assertEqual(result["normalized_R2_cross_edges"], [[0, 0], [1, 1]])

    def test_exact_four_transversal_candidates(self) -> None:
        result = check.actual_incidence_board()
        self.assertEqual(result["transversal_candidate_count"], 4)
        self.assertEqual(
            result["transversal_candidates"],
            [
                ["w00", "w11", "w22a"],
                ["w00", "w11", "w22b"],
                ["w00", "w12", "w21"],
                ["w02", "w11", "w20"],
            ],
        )

    def test_mu_three_mutation_changes_board_and_candidate_count(self) -> None:
        hostile = check.actual_incidence_board()["hostile_mu_3"]
        self.assertEqual(hostile["transversal_candidate_count"], 22)
        self.assertFalse(hostile["passes_target_count"])

    def test_local_zero_and_one_motif_controls(self) -> None:
        result = check.local_incidence_nonforcing()
        zero = result["zero_motif_control"]
        one = result["one_motif_control"]
        self.assertEqual(zero["common_R3_count"], 0)
        self.assertEqual(one["common_R3_count"], 1)
        self.assertEqual(zero["R2_pair_trace_contribution"], 0)
        self.assertEqual(one["R2_pair_trace_contribution"], 2)
        self.assertEqual(
            zero["cross_pair_common_neighbor_board"],
            one["cross_pair_common_neighbor_board"],
        )
        self.assertTrue(result["shared_exact_cross_pair_lambda_mu"])

    def test_local_controls_fail_global_scope(self) -> None:
        result = check.local_incidence_nonforcing()
        for name in ("zero_motif_control", "one_motif_control"):
            control = result[name]
            self.assertEqual(
                control["status"],
                "LOCAL_CROSS_PAIR_CONTROL_NOT_A_TARGET_GRAPH",
            )
            self.assertEqual(control["vertex_count"], 14)
            self.assertIn("99-vertex size and degree 14", control["dropped_premises"])

    def test_status_wall(self) -> None:
        status = check.status_wall()
        self.assertEqual(status["global_motif_forcing"], "UNKNOWN")
        self.assertEqual(status["global_motif_avoidance"], "UNKNOWN")
        self.assertEqual(status["n3_708"], "UNKNOWN")
        self.assertEqual(status["Conway_99"], "UNKNOWN")

    def test_deterministic_json(self) -> None:
        expected = check.canonical_bytes(check.build_results())
        parsed = json.loads(expected)
        self.assertEqual(parsed["schema_version"], 1)
        self.assertFalse(parsed["independence"]["candidate_files_inspected"])
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "precomparison.json"
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
