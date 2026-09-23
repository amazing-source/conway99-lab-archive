from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from pathlib import Path

import exact_check as check


class RootedExtensionTests(unittest.TestCase):
    def test_frozen_inputs(self) -> None:
        self.assertEqual(check.verify_frozen_inputs(), check.FROZEN_INPUTS)

    def test_fixed_support_and_label_multiplicity(self) -> None:
        result = check.fixed_support_identities()
        self.assertTrue(result["fixed_SS_block_identity"])
        self.assertEqual(result["rank_F"], 13)
        self.assertEqual(result["rank_FFt"], 13)
        self.assertEqual(
            result["O_label_types"],
            {
                "support_edge_completion": 28,
                "support_nonedge_completion": 42,
            },
        )
        self.assertTrue(result["signed_minus_four_vector_in_kernel_Ft"])

    def test_equitable_partition(self) -> None:
        result = check.equitable_partition()
        self.assertEqual(result["cell_sizes"], [14, 70, 15])
        self.assertEqual(
            result["quotient"],
            [[4, 10, 0], [2, 9, 3], [0, 14, 0]],
        )
        self.assertTrue(result["Q_is_independent"])
        self.assertEqual(
            result["quotient_characteristic_polynomial"],
            "(x-14)(x-3)(x+4)",
        )

    def test_mu_two_is_active(self) -> None:
        hostile = check.equitable_partition()["hostile_mu_3"]
        self.assertEqual(hostile["implied_Q_to_O_degree"], 21)
        self.assertEqual(hostile["available_total_degree"], 14)
        self.assertFalse(hostile["passes"])

    def test_design_and_two_factor_cycle_types(self) -> None:
        result = check.design_consequences()
        self.assertEqual(result["design"], "simple 2-(15,3,2) with 70 blocks")
        self.assertEqual(
            result["each_Q_neighborhood_label_graph"]["cycle_types"],
            [[14], [10, 4], [8, 6], [6, 4, 4]],
        )
        centered = result["scaled_centered_neighborhood_vectors"]
        self.assertEqual(centered["gram_diagonal"], 280)
        self.assertEqual(centered["gram_off_diagonal"], -20)
        self.assertEqual(centered["span_dimension"], 14)

    def test_hostile_abstract_design_is_exact_but_insufficient(self) -> None:
        result = check.hostile_design_only_control()
        self.assertEqual(
            result["status"],
            "HOSTILE_DESIGN_ONLY_NOT_AN_EXTENSION",
        )
        self.assertEqual(result["block_count"], 70)
        self.assertTrue(result["blocks_are_distinct"])
        self.assertEqual(result["row_weight_histogram"], {"3": 70})
        self.assertEqual(result["column_weight_histogram"], {"14": 15})
        self.assertEqual(result["pairwise_column_intersections"], [2])
        self.assertTrue(result["B_transpose_B_passes"])
        self.assertFalse(result["F_B_equals_2J"])
        self.assertGreater(result["arbitrary_O_label_order_FB_mismatch_count"], 0)

    def test_forced_support_star_edges(self) -> None:
        adjacency = check.build_forced_support_star_edges()
        self.assertEqual(check.degree_histogram(adjacency), {"0": 28, "2": 42})
        self.assertEqual(sum(sum(row) for row in adjacency) // 2, 42)
        self.assertEqual(adjacency, check.transpose(adjacency))
        self.assertTrue(all(adjacency[i][i] == 0 for i in range(70)))

    def test_extension_criterion_schema(self) -> None:
        result = check.extension_criterion()
        self.assertEqual(len(result["block_equations"]), 6)
        self.assertIn("necessarily", result["necessity"].lower())
        self.assertIn("simple 99-vertex", result["sufficiency"])
        self.assertEqual(
            result["finite_search_space"]["total_raw_binary_variables"],
            3465,
        )
        self.assertEqual(
            result["finite_search_space"]["automorphism_assumption"],
            "none",
        )

    def test_hostile_partial_pair_is_rejected(self) -> None:
        result = check.extension_criterion()["hostile_partial_control"]
        self.assertEqual(result["D_edge_count"], 42)
        self.assertEqual(result["status"], "REJECTED_BY_COMPLETE_CRITERION")
        diagnostics = result["criterion_diagnostics"]
        self.assertTrue(diagnostics["shape_and_binary"])
        self.assertTrue(diagnostics["D_symmetric_zero_diagonal"])
        self.assertTrue(diagnostics["block_passes"]["SS_fixed"])
        self.assertTrue(diagnostics["block_passes"]["QQ"])
        self.assertFalse(diagnostics["block_passes"]["SQ"])
        self.assertFalse(diagnostics["all_blocks_pass"])
        self.assertFalse(diagnostics["assembled_global_identity_passes"])

    def test_shape_mutation_is_rejected(self) -> None:
        diagnostics = check.extension_criterion_diagnostics(
            check.zeros(69, 69),
            check.zeros(70, 15),
        )
        self.assertFalse(diagnostics["shape_and_binary"])
        self.assertFalse(diagnostics["all_blocks_pass"])

    def test_quadratic_exact_arithmetic(self) -> None:
        # (-1+sqrt(2))^2=3-2sqrt(2), and conjugate sums are integral.
        self.assertEqual(check.quadratic_power(-1, 1, 2), (3, -2))
        self.assertEqual(check.quadratic_power(-1, -1, 2), (3, 2))
        for exponent in range(5):
            self.assertIsInstance(check.forced_D_spectral_moment(exponent), int)

    def test_forced_O_graph_spectrum_and_cycles(self) -> None:
        result = check.forced_D_spectrum()
        self.assertEqual(
            result["spectrum"],
            {
                "9": 1,
                "-1": 14,
                "-1-sqrt(2)": 6,
                "-1+sqrt(2)": 6,
                "3": 27,
                "-4": 16,
            },
        )
        self.assertEqual(
            result["spectral_moments"],
            {"0": 70, "1": 0, "2": 630, "3": 336, "4": 13062},
        )
        self.assertTrue(result["connected"])
        self.assertEqual(result["edge_count"], 315)
        self.assertEqual(result["triangle_count"], 56)
        self.assertEqual(result["four_cycle_count"], 294)
        self.assertEqual(result["determinant"], "2^32*3^29")

    def test_triangle_and_edge_partition(self) -> None:
        result = check.triangle_and_edge_census()
        self.assertEqual(
            result["D_edge_partition_by_unique_common_neighbor_cell"],
            {"S": 42, "Q": 105, "O": 168, "total": 315},
        )
        self.assertEqual(
            result["target_triangle_partition"],
            {
                "two_S_one_O": 28,
                "one_S_two_O": 42,
                "two_O_one_Q": 105,
                "three_O": 56,
            },
        )
        self.assertEqual(result["target_graph"]["triangle_count"], 231)

    def test_status_wall(self) -> None:
        result = check.build_results()
        self.assertFalse(result["status"]["full_extension_found"])
        self.assertEqual(result["status"]["root_exclusion"], "NOT_OBTAINED")
        self.assertEqual(result["status"]["Conway_99"], "UNKNOWN")
        self.assertTrue(
            any("No complete search" in limitation for limitation in result["limitations"])
        )

    def test_deterministic_json(self) -> None:
        expected = check.canonical_bytes(check.build_results())
        parsed = json.loads(expected)
        self.assertEqual(parsed["schema_version"], 1)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "result.json"
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
