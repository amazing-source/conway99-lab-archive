#!/usr/bin/env python3
"""Adversarial tests for the clean-room Wave 33 rooted verifier."""

from __future__ import annotations

import copy
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

import independent_check


class Wave33RootedExtensionVerifierTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = independent_check.build_result()
        cls.f_matrix = cls.result["support"]["support_adjacency"]
        cls.d_matrix = cls.result["support_outside_incidence"]["D"]

    def test_frozen_inputs_and_precomparison_status(self) -> None:
        self.assertEqual(self.result["inputs"], independent_check.FROZEN_INPUTS)
        self.assertEqual(self.result["comparison_status"], "NOT_RELEASED")
        self.assertFalse(self.result["imports_or_executes_candidate_code"])

    def test_fano_design_is_derived_not_catalogued(self) -> None:
        support = self.result["support"]
        self.assertEqual(len(support["fano_lines"]), 7)
        pairs = {
            pair: sum(set(pair).issubset(line) for line in support["fano_lines"])
            for pair in __import__("itertools").combinations(range(1, 8), 2)
        }
        self.assertEqual(set(pairs.values()), {1})
        self.assertEqual(
            independent_check.row_sums(support["cross_matrix"]), [4] * 7
        )
        self.assertFalse(support["uses_catalog"])
        self.assertFalse(support["uses_automorphism"])

    def test_support_graph_is_simple_four_regular(self) -> None:
        f_matrix = self.f_matrix
        self.assertEqual(f_matrix, independent_check.transpose(f_matrix))
        self.assertEqual(independent_check.row_sums(f_matrix), [4] * 14)
        self.assertTrue(all(f_matrix[i][i] == 0 for i in range(14)))
        self.assertEqual(
            self.result["support"]["support_spectrum"],
            {
                "4": 1,
                "-4": 1,
                "+sqrt(2)": 6,
                "-sqrt(2)": 6,
            },
        )

    def test_D_is_the_complete_support_completion_incidence(self) -> None:
        d_data = self.result["support_outside_incidence"]
        self.assertEqual(d_data["shape"], [14, 70])
        self.assertEqual(d_data["row_sums"], [10] * 14)
        self.assertEqual(d_data["column_sums"], [2] * 70)
        self.assertEqual(
            d_data["type_counts"],
            {
                "support_edge_completion": 28,
                "support_cross_nonedge_completion": 42,
            },
        )
        self.assertEqual(d_data["rank"], 13)

    def test_SS_block_identity_and_signed_kernel(self) -> None:
        f_squared = independent_check.matmul(self.f_matrix, self.f_matrix)
        dd_t = independent_check.matmul(
            self.d_matrix, independent_check.transpose(self.d_matrix)
        )
        lhs = independent_check.matrix_add(f_squared, dd_t)
        rhs = independent_check.matrix_add(
            independent_check.matrix_scale(independent_check.identity(14), 12),
            independent_check.matrix_scale(self.f_matrix, -1),
            independent_check.matrix_scale(independent_check.ones(14, 14), 2),
        )
        self.assertEqual(lhs, rhs)
        signed = [1] * 7 + [-1] * 7
        self.assertEqual(
            [
                sum(self.d_matrix[i][j] * signed[i] for i in range(14))
                for j in range(70)
            ],
            [0] * 70,
        )

    def test_quotient_is_derived_without_assumption(self) -> None:
        quotient = self.result["quotient"]
        self.assertEqual(quotient["cell_sizes"], [14, 70, 15])
        self.assertEqual(
            quotient["quotient"],
            [[4, 10, 0], [2, 9, 3], [0, 14, 0]],
        )
        self.assertTrue(quotient["Q_independent"])
        self.assertFalse(quotient["equitability_assumed"])
        self.assertEqual(
            quotient["common_neighbour_double_counts"]["for_o_in_O"][
                "sum_over_s_in_S"
            ],
            26,
        )
        self.assertEqual(
            quotient["common_neighbour_double_counts"]["for_q_in_Q"][
                "sum_over_s_in_S"
            ],
            28,
        )

    def test_quotient_spectrum_and_balance(self) -> None:
        quotient = self.result["quotient"]
        self.assertEqual(
            quotient["quotient_spectrum"], {"14": 1, "3": 1, "-4": 1}
        )
        matrix = quotient["quotient"]
        sizes = quotient["cell_sizes"]
        for left, right in ((0, 1), (1, 2), (0, 2)):
            self.assertEqual(
                sizes[left] * matrix[left][right],
                sizes[right] * matrix[right][left],
            )

    def test_design_parameters_and_simplicity(self) -> None:
        design = self.result["O_Q_design"]
        self.assertEqual(design["B_shape"], [70, 15])
        self.assertEqual(design["B_row_weight"], 3)
        self.assertEqual(design["B_column_weight"], 14)
        self.assertEqual(design["pair_lambda"], 2)
        self.assertEqual(design["design"], "simple 2-(15,3,2)")
        self.assertIn("at least three", design["simplicity_argument"])

    def test_all_six_block_equations_are_present(self) -> None:
        equations = self.result["finite_binary_criterion"]["block_equations"]
        self.assertEqual(set(equations), {"SS", "SO", "SQ", "OO", "OQ", "QQ"})
        self.assertEqual(equations["SQ"], "D*B=2J_(14x15)")
        self.assertEqual(equations["QQ"], "B^T*B=12I_15+2J_15")
        self.assertIn("H^2", equations["OO"])

    def test_full_residual_equals_six_block_residuals(self) -> None:
        b_matrix, h_matrix = independent_check.deterministic_hostile_matrices()
        adjacency = independent_check.assemble_adjacency(
            self.f_matrix, self.d_matrix, b_matrix, h_matrix
        )
        full = independent_check.matrix_subtract(
            independent_check.matmul(adjacency, adjacency),
            independent_check.rhs_srg(adjacency),
        )
        blocks = independent_check.block_residuals(
            self.f_matrix, self.d_matrix, b_matrix, h_matrix
        )
        ranges = {
            "SS": (0, 14, 0, 14),
            "SO": (0, 14, 14, 84),
            "SQ": (0, 14, 84, 99),
            "OO": (14, 84, 14, 84),
            "OQ": (14, 84, 84, 99),
            "QQ": (84, 99, 84, 99),
        }
        for name, bounds in ranges.items():
            self.assertEqual(
                independent_check.extract_block(full, *bounds), blocks[name]
            )

    def test_hostile_binary_matrices_fail_closed(self) -> None:
        b_matrix, h_matrix = independent_check.deterministic_hostile_matrices()
        evaluation = independent_check.evaluate_binary_criterion(
            self.f_matrix, self.d_matrix, b_matrix, h_matrix
        )
        self.assertFalse(evaluation["passes"])
        self.assertTrue(evaluation["gates"]["B_binary"])
        self.assertTrue(evaluation["gates"]["H_binary"])
        self.assertTrue(evaluation["gates"]["H_symmetric"])
        self.assertTrue(evaluation["gates"]["H_zero_diagonal"])
        self.assertTrue(
            any(count for count in evaluation["block_residual_nonzero_entries"].values())
        )

    def test_duplicate_design_rows_are_rejected(self) -> None:
        b_matrix = [[0] * 15 for _ in range(70)]
        for row in range(70):
            for column in (row % 15, (row + 1) % 15, (row + 4) % 15):
                b_matrix[row][column] = 1
        b_matrix[1] = b_matrix[0][:]
        h_matrix = independent_check.zeros(70, 70)
        evaluation = independent_check.evaluate_binary_criterion(
            self.f_matrix, self.d_matrix, b_matrix, h_matrix
        )
        self.assertFalse(evaluation["gates"]["B_rows_distinct"])
        self.assertFalse(evaluation["passes"])

    def test_H_loop_and_asymmetry_are_active_gates(self) -> None:
        b_matrix, h_matrix = independent_check.deterministic_hostile_matrices()
        looped = copy.deepcopy(h_matrix)
        looped[0][0] = 1
        evaluation = independent_check.evaluate_binary_criterion(
            self.f_matrix, self.d_matrix, b_matrix, looped
        )
        self.assertFalse(evaluation["gates"]["H_zero_diagonal"])
        asymmetric = copy.deepcopy(h_matrix)
        asymmetric[0][1] ^= 1
        evaluation = independent_check.evaluate_binary_criterion(
            self.f_matrix, self.d_matrix, b_matrix, asymmetric
        )
        self.assertFalse(evaluation["gates"]["H_symmetric"])

    def test_H_spectrum_dimensions_and_moments(self) -> None:
        spectrum = self.result["H_spectrum"]
        self.assertEqual(
            sum(item["multiplicity"] for item in spectrum["spectrum"]), 70
        )
        self.assertEqual(spectrum["rank_D"], 13)
        self.assertEqual(spectrum["rank_B"], 15)
        self.assertEqual(spectrum["trace"], 0)
        self.assertEqual(spectrum["trace_H_squared"], 630)
        self.assertEqual(spectrum["edge_count"], 315)
        self.assertEqual(spectrum["trace_H_cubed"], 336)
        self.assertEqual(spectrum["triangle_count"], 56)

    def test_H_residual_multiplicities(self) -> None:
        multiplicities = {
            item["eigenvalue"]: item["multiplicity"]
            for item in self.result["H_spectrum"]["spectrum"]
        }
        self.assertEqual(multiplicities["3"], 27)
        self.assertEqual(multiplicities["-4"], 16)
        self.assertEqual(multiplicities["-1"], 14)
        self.assertEqual(multiplicities["-1+sqrt(2)"], 6)
        self.assertEqual(multiplicities["-1-sqrt(2)"], 6)

    def test_no_automorphism_scope(self) -> None:
        criterion = self.result["finite_binary_criterion"]
        self.assertIn("no automorphism restriction", criterion["finite_search_space"])
        self.assertFalse(self.result["uses_automorphism_restriction"])
        self.assertIn(
            "Forbidden and unnecessary",
            self.result["hostile_premise_checks"][
                "assume_support_automorphism_extends"
            ],
        )

    def test_status_wall(self) -> None:
        status = self.result["status"]
        for key in (
            "cell_sizes_and_quotient",
            "Q_independent",
            "simple_2_15_3_2_design",
            "block_criterion_necessity",
            "block_criterion_sufficiency",
            "conditional_H_spectrum",
        ):
            self.assertEqual(status[key], "DERIVED")
        for key in (
            "criterion_has_binary_solution",
            "rooted_endpoint_extension_or_exclusion",
            "n3_708",
            "Conway_99",
            "novelty",
        ):
            self.assertEqual(status[key], "UNKNOWN")

    def test_canonical_json_is_deterministic_and_lf_only(self) -> None:
        first = independent_check.render(self.result)
        second = independent_check.render(independent_check.build_result())
        self.assertEqual(first, second)
        self.assertTrue(first.endswith("\n"))
        self.assertNotIn("\r", first)
        self.assertEqual(json.loads(first), self.result)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "independent.json"
            independent_check.write_json(path, self.result)
            payload = path.read_bytes()
        self.assertEqual(payload, first.encode("utf-8"))
        self.assertEqual(
            hashlib.sha256(payload).hexdigest(),
            hashlib.sha256(first.encode("utf-8")).hexdigest(),
        )


if __name__ == "__main__":
    unittest.main()
