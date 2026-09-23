from __future__ import annotations

import json
import tempfile
import unittest
from fractions import Fraction
from pathlib import Path

import exact_check


class CleanRoomStructuralTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = exact_check.build_result()

    def test_frozen_inputs(self) -> None:
        self.assertTrue(self.result["input_integrity"]["all_hashes_pass"])
        self.assertEqual(
            self.result["input_integrity"]["files"],
            exact_check.INPUT_HASHES,
        )

    def test_fixed_support_is_reconstructed_exactly(self) -> None:
        fixed = exact_check.fixed_linear_algebra()
        self.assertEqual(fixed["rank_F"], 13)
        self.assertEqual(fixed["rank_P_F"], 13)
        self.assertEqual(fixed["trace_T"], "140")
        self.assertEqual(
            fixed["support_overlap_by_type"]["support_edge"],
            {"g0": 51, "g1": 18, "g2": 0},
        )
        self.assertEqual(
            fixed["support_overlap_by_type"]["support_nonedge_copy"],
            {"g0": 52, "g1": 16, "g2": 1},
        )

    def test_fixed_projector_is_exact(self) -> None:
        fixed = exact_check.fixed_linear_algebra()
        projector = fixed["P_F"]
        self.assertEqual(exact_check.matmul(projector, projector), projector)
        self.assertEqual(exact_check.trace(projector), Fraction(13))
        self.assertEqual(
            fixed["P_F_diagonal_by_type"],
            {
                "support_edge": "97/490",
                "support_nonedge_copy": "87/490",
            },
        )

    def test_bad_projector_division_is_rejected(self) -> None:
        fixed = exact_check.fixed_linear_algebra()
        mutated = exact_check.fixed_support_projector(
            fixed["T"],
            denominator=1961,
        )
        self.assertNotEqual(exact_check.matmul(mutated, mutated), mutated)

    def test_universal_spectral_decomposition(self) -> None:
        audit = self.result["universal_spectral_audit"]
        self.assertEqual(audit["dimension_row_space_F_plus_B"], 27)
        self.assertEqual(audit["dimension_W"], 43)
        self.assertEqual(audit["trace_K"], "17")
        self.assertEqual(audit["rank_E_3"], "27")
        self.assertEqual(audit["rank_E_minus_4"], "16")

    def test_projector_diagonal_leverages(self) -> None:
        diagonal = self.result["D_residual_decomposition"][
            "projector_diagonal_by_support_type"
        ]
        self.assertEqual(diagonal["support_edge"]["E_3"], "39/98")
        self.assertEqual(diagonal["support_edge"]["E_minus_4"], "10/49")
        self.assertEqual(
            diagonal["support_nonedge_copy"]["E_3"],
            "37/98",
        )
        self.assertEqual(
            diagonal["support_nonedge_copy"]["E_minus_4"],
            "12/49",
        )

    def test_global_projector_principal_ranks(self) -> None:
        projectors = self.result["global_projector_principal_blocks"]
        self.assertEqual(projectors["P3_OO_rank"], 54)
        self.assertEqual(projectors["P3_OO_nullity"], 16)
        self.assertEqual(projectors["Pminus4_OO_rank"], 43)
        self.assertEqual(projectors["Pminus4_OO_nullity"], 27)

    def test_nine_pair_states_are_exhaustive(self) -> None:
        states = exact_check.allowed_pair_states()
        self.assertEqual(len(states), 9)
        self.assertEqual(
            {state.support_overlap + state.q_overlap
             + state.adjacent + state.common_o for state in states},
            {2},
        )

    def test_pair_distribution_is_uniquely_forced(self) -> None:
        pair = self.result["forced_pair_distribution"]
        self.assertEqual(pair["constraint_matrix_rank"], 9)
        self.assertEqual(
            pair["row_distribution_by_support_type"]["support_edge"][
                "g1_r1_h0_c0"
            ],
            6,
        )
        self.assertEqual(
            pair["row_distribution_by_support_type"][
                "support_nonedge_copy"
            ]["g1_r1_h0_c0"],
            6,
        )
        self.assertEqual(
            sum(pair["global_unordered_pair_distribution"].values()),
            2415,
        )

    def test_tr_diagonal_mutation_breaks_x11_degree(self) -> None:
        mutated = exact_check.solve_pair_distribution(
            support_type="support_edge",
            tr_diagonal=11,
        )
        self.assertEqual(mutated["g1_r1_h0_c0"], 5)
        self.assertNotEqual(mutated["g1_r1_h0_c0"], 6)

    def test_forced_graph_census(self) -> None:
        graphs = self.result["forced_pair_distribution"]["forced_graphs"]
        self.assertEqual(
            graphs["support_and_Q_single_overlap_X11"]["degree"],
            6,
        )
        self.assertEqual(
            graphs["support_and_Q_single_overlap_X11"]["edges"],
            210,
        )
        self.assertEqual(
            graphs["double_Q_overlap_R2"]["edges"],
            105,
        )
        self.assertEqual(
            graphs["duplicate_support_label_G2"]["edges"],
            21,
        )
        self.assertEqual(
            graphs["D_edges_common_neighbor_in_O"]["triangles"],
            56,
        )

    def test_no_symmetry_restriction_or_status_inflation(self) -> None:
        domain = self.result["domain"]
        self.assertFalse(domain["automorphism_assumed"])
        self.assertFalse(domain["orbit_representative_assumed"])
        self.assertFalse(domain["fixed_O_Q_design_assumed"])
        status = self.result["status"]
        self.assertEqual(status["stage_1_reconstruction"], "DERIVED")
        self.assertFalse(status["wave34_candidate_seen"])
        self.assertEqual(
            status["rooted_graph_extension_or_exclusion"],
            "UNKNOWN",
        )

    def test_deterministic_lf_json(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            first = Path(directory) / "first.json"
            second = Path(directory) / "second.json"
            exact_check.write_json_lf(first, exact_check.build_result())
            exact_check.write_json_lf(second, exact_check.build_result())
            self.assertEqual(first.read_bytes(), second.read_bytes())
            self.assertNotIn(b"\r\n", first.read_bytes())
            self.assertEqual(json.loads(first.read_text("utf-8")), self.result)


if __name__ == "__main__":
    unittest.main()
