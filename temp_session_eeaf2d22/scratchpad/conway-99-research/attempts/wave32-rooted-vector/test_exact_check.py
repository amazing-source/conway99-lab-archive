from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from pathlib import Path

import exact_check as check


class RootedVectorTests(unittest.TestCase):
    def test_frozen_inputs(self) -> None:
        self.assertEqual(check.verify_frozen_inputs(), check.FROZEN_INPUTS)

    def test_extreme_fiber_psd_census(self) -> None:
        result = check.extreme_fiber_screen()
        self.assertEqual(result["maximum_same_sign_fiber_size"], 3)
        self.assertEqual(result["psd_gram_count_by_fiber_size"]["4"], 0)
        self.assertEqual(result["size_three_relation"], "u1+u2+u3=0")
        self.assertEqual(result["opposite_extreme_frame_products_if_triple"], [-2] * 3)

    def test_root_pattern_counts(self) -> None:
        result = check.root_count_patterns()
        self.assertEqual(
            result["counts"],
            {
                "moment_only": 46,
                "wave28_tensor_filtered": 32,
                "matrix_only_extreme_filtered": 16,
                "actual_incidence_filtered": 1,
            },
        )

    def test_projector_transport_coefficients(self) -> None:
        result = check.projector_and_incidence_transport()
        self.assertEqual(result["projector_eigenvalues"]["minus_4"], "1")
        self.assertIn("all 99 coordinates", result["consequence"])

    def test_mod_three_residue_screen(self) -> None:
        result = check.residue_reduction()
        accepted = [
            row["residue"] for row in result["cases"] if row["accepted"]
        ]
        self.assertEqual(accepted, [0])

    def test_integer_minus_four_amplitude_screen(self) -> None:
        result = check.eigenvector_amplitude_screen()
        self.assertEqual(result["raw_integer_distribution_count"], 12)
        self.assertEqual(result["surviving_distribution_count"], 1)
        self.assertEqual(result["survivors"], [{"-1": 7, "0": 85, "1": 7}])

    def test_hostile_minus_three_is_active(self) -> None:
        result = check.eigenvector_amplitude_screen(3)
        self.assertEqual(result["surviving_distribution_count"], 3)
        self.assertEqual(result["coordinate_bound_abs_values"], [0, 1, 2])
        self.assertTrue(
            any(
                "3*m<=positive_mass" in inequality
                for inequality in result["proof_inequalities"]
            )
        )

    def test_support_design_forcing(self) -> None:
        result = check.support_design_screen()
        self.assertEqual(result["passing_t"], [0])
        self.assertEqual(result["row_sums"], [4] * 7)
        self.assertEqual(result["same_side_pair_intersections"], [2])

    def test_mu_two_is_active(self) -> None:
        result = check.support_design_screen(3)
        self.assertEqual(result["passing_t"], [0, 1, 2])

    def test_final_hostile_pattern_and_outside_census(self) -> None:
        result = check.final_y_and_outside_census()
        self.assertEqual(
            result["root_triangle_vector_y"],
            {
                "plus_2": 0,
                "plus_1": 21,
                "zero": 189,
                "minus_1": 21,
                "minus_2": 0,
            },
        )
        self.assertEqual(sum(result["outside_vertex_types"].values()), 85)

    def test_schur_and_a4_constraints(self) -> None:
        result = check.schur_and_a4_constraints()
        self.assertEqual(
            result["double_contraction"]["possible_g2"],
            [6, 14, 22, 30, 38, 46, 54, 62, 70, 78],
        )
        self.assertEqual(result["first_contraction"]["possible_H2"][-1], 78)
        self.assertEqual(result["A4"]["identity"], "y^T A4 y=441*H2")

    def test_root_reflection_scope_wall(self) -> None:
        result = check.root_reflection()
        self.assertIn("not graph automorphisms", result["status_wall"])

    def test_hostile_partial_control(self) -> None:
        result = check.build_hostile_partial_control()
        self.assertEqual(result["status"], "PARTIAL_LOCAL_CONTROL_NOT_A_GRAPH")
        self.assertEqual(result["support_degrees"], [14] * 14)
        self.assertEqual(
            result["outside_support_degree_distribution"],
            {"0": 15, "2": 70},
        )
        self.assertEqual(
            result["outside_total_degree_distribution"],
            {"0": 15, "2": 28, "4": 42},
        )
        self.assertEqual(
            result["outside_remaining_degree_distribution"],
            {"10": 42, "12": 28, "14": 15},
        )
        self.assertIn("degrees 10, 12, or 14", result["unfilled_boundary"])
        self.assertEqual(
            result["support_pair_common_neighbor_values"],
            {"edge": [1], "nonedge": [2]},
        )
        self.assertEqual(result["forced_singleton_triangle_edge_count"], 42)

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
