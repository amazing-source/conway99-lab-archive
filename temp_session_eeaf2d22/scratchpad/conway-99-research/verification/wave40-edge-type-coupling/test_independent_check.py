"""Hostile and exact tests for the clean-room Wave 40 verifier."""

from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).with_name("independent_check.py")
SPEC = importlib.util.spec_from_file_location("wave40_edge_coupling", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
CHECK = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CHECK)


class IndependentEdgeCouplingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = CHECK.build_results()

    def test_six_point_pairings_and_relative_types_are_complete(self) -> None:
        self.assertEqual(len(CHECK.PAIRINGS), 15)
        counts = {}
        for pairing in CHECK.PAIRINGS:
            kind = CHECK.pairing_union_type(CHECK.BASE_PAIRING, pairing)
            counts[kind] = counts.get(kind, 0) + 1
        self.assertEqual(counts, {(1, 1, 1): 1, (1, 2): 6, (3,): 8})

    def test_normalization_count_is_4050_not_one_relation(self) -> None:
        normalized = self.result["normalized_quotient_enumeration"]
        self.assertEqual(normalized["representative_count"], 4050)
        self.assertNotEqual(normalized["representative_count"], 1350)
        self.assertIn("not asserted", normalized["isomorphism_warning"])

    def test_exact_f3_rank_distribution_and_eight_boundary_cases(self) -> None:
        normalized = self.result["normalized_quotient_enumeration"]
        self.assertEqual(
            normalized["rank_distribution"],
            {"11": 8, "12": 1, "13": 400, "14": 46, "15": 2616, "16": 979},
        )
        self.assertEqual(normalized["rank_eleven_count"], 8)

    def test_wrong_quotient_diagonal_is_rejected(self) -> None:
        quotient = CHECK.canonical_rank_eleven_quotient()
        wrong = CHECK.adjacency_matrix(quotient)
        for index in range(len(wrong)):
            wrong[index][index] = 1
        self.assertNotEqual(CHECK.matrix_rank(wrong, 3), 11)

    def test_explicit_quotient_shape(self) -> None:
        quotient = self.result["explicit_rank_eleven_quotient"]
        self.assertEqual(quotient["vertex_count"], 18)
        self.assertEqual(quotient["edge_count"], 36)
        self.assertEqual(quotient["degree_set"], [4])
        self.assertEqual(quotient["rank_F3_2I_plus_A_Q"], 11)

    def test_all_endpoint_pairing_masks_are_covered(self) -> None:
        lifts = self.result["endpoint_pairing_lifts"]
        self.assertEqual(lifts["mask_count"], 2**18)
        self.assertEqual(lifts["quotient_triangle_count"], 16)
        self.assertEqual(lifts["triangle_free_mask_count"], 37378)

    def test_exact_f7_lift_rank_distribution(self) -> None:
        self.assertEqual(
            self.result["endpoint_pairing_lifts"][
                "rank_F7_3I_minus_A_X_distribution"
            ],
            {"32": 264, "33": 7348, "34": 29766},
        )
        self.assertEqual(
            self.result["endpoint_pairing_lifts"][
                "rank_F7_39_block_K_distribution"
            ],
            {"33": 264, "34": 7348, "35": 29766},
        )

    def test_canonical_positive_control(self) -> None:
        witness = self.result["endpoint_pairing_lifts"][
            "canonical_minimum_rank_witness"
        ]
        self.assertEqual(witness["x_vertex_count"], 36)
        self.assertEqual(witness["x_edge_count"], 54)
        self.assertEqual(witness["x_degree_set"], [3])
        self.assertEqual(witness["x_triangle_count"], 0)
        self.assertEqual(
            witness["base_edge_types"],
            {"01": [2, 2, 2], "12": [2, 2, 2], "20": [2, 2, 2]},
        )
        self.assertEqual(witness["rank_F7_3I_minus_A_X"], 32)

    def test_sparse_rank_matches_dense_on_witness(self) -> None:
        quotient = CHECK.canonical_rank_eleven_quotient()
        assignments = CHECK.half_edge_assignments(quotient)
        mask = self.result["endpoint_pairing_lifts"][
            "canonical_minimum_rank_witness"
        ]["mask_integer"]
        adjacency = CHECK.lifted_x_adjacency(quotient, assignments, mask)
        self.assertEqual(
            CHECK.sparse_rank_three_i_minus_adjacency(adjacency),
            CHECK.matrix_rank(CHECK.three_i_minus_adjacency(adjacency), 7),
        )

    def test_exact_39_block_identity(self) -> None:
        identity = self.result["rank_39_identity"]["canonical_witness_check"]
        self.assertEqual(identity["rank_F7_3I_minus_A_X"], 32)
        self.assertEqual(identity["rank_F7_K_39"], 33)
        self.assertEqual(
            identity["rank_F7_K_39"],
            1 + identity["rank_F7_3I_minus_A_X"],
        )

    def test_global_face_handshake_and_euler_scope(self) -> None:
        complex_data = self.result["global_complex"]
        self.assertEqual(complex_data["endpoint_bijection"]["E_J"], 4158)
        self.assertEqual(complex_data["endpoint_bijection"]["E_L"], 4158)
        self.assertEqual(
            complex_data["closed_complex"]["unsplit_chi_range"],
            [-3234, -1848],
        )
        self.assertEqual(
            complex_data["normalized_surface"]["coarse_chi_range"],
            [-3234, -693],
        )
        self.assertIn(
            "not automatically",
            complex_data["closed_complex"]["surface_warning"],
        )

    def test_status_cannot_be_inflated(self) -> None:
        status = self.result["status_wall"]
        self.assertEqual(status["endpoint_n3_4158"], "UNKNOWN")
        self.assertEqual(status["general_upper_bound_below_4158"], "NOT_PROVED")
        self.assertEqual(status["conway_99"], "UNKNOWN")
        self.assertEqual(status["graph_or_counterexample"], "NONE")
        self.assertEqual(status["novelty_or_priority"], "UNKNOWN")

    def test_positive_control_is_explicitly_local(self) -> None:
        control = self.result["positive_control"]
        self.assertEqual(control["status"], "VERIFIED_ONE_TRIANGLE_CONTROL")
        self.assertIn(
            "a 99-vertex strongly regular graph", control["not_supplied"]
        )
        self.assertIn(
            "cross-triangle compatibility", control["not_supplied"]
        )


if __name__ == "__main__":
    unittest.main()
