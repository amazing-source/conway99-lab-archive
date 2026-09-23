from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from pathlib import Path

import independent_check as check


class IndependentRootedVectorTests(unittest.TestCase):
    def test_frozen_bytes(self) -> None:
        self.assertEqual(check.verify_frozen(), check.FROZEN)
        manifest = check.verify_discovery_v2_manifest()
        self.assertEqual(manifest["status"], "PASS")
        self.assertEqual(manifest["entry_count"], 8)
        self.assertEqual(
            manifest["manifest_sha256"],
            "ba6c7099e06e24fe2feee4d19021dac9ddf49cbfe99acdd54f905a6c40728b8e",
        )
        repairs = check.verify_discovery_v2_repairs()
        self.assertEqual(repairs["status"], "PASS")
        self.assertEqual(
            repairs["remaining_degree_distribution"],
            {"10": 42, "12": 28, "14": 15},
        )

    def test_primitive_transpose_bridge_and_hostile_control(self) -> None:
        result = check.primitive_image_controls()
        self.assertEqual(result["primitive_maximal_minor_gcd"], 1)
        self.assertEqual(result["explicit_transpose_images"], [[1, 0], [0, 1]])
        self.assertEqual(result["hostile_nonprimitive_maximal_minor_gcd"], 2)
        self.assertFalse(result["hostile_target_has_integral_preimage"])

    def test_projector_and_mod_three_transport(self) -> None:
        result = check.projector_transport()
        self.assertEqual(
            result["projector_values"],
            {"14": "0", "3": "0", "-4": "1"},
        )
        self.assertEqual(result["incidence_column_sum"], 3)
        self.assertEqual(set(result["mod_3_column"]), {1})

    def test_residue_elimination(self) -> None:
        rows = check.residue_screen()["cases"]
        self.assertEqual(
            [row["residue"] for row in rows if row["accepted_by_integer_norm_bound"]],
            [0],
        )
        self.assertEqual([row["norm_k_squared"] for row in rows], [25, 14, 25])

    def test_norm_constant_is_active(self) -> None:
        rows = check.residue_screen(198)["cases"]
        self.assertEqual(
            [row["residue"] for row in rows if row["accepted_by_integer_norm_bound"]],
            [-1, 0, 1],
        )

    def test_minus_four_amplitude_and_seven_plus_seven(self) -> None:
        result = check.amplitude_screen()
        self.assertEqual(result["raw_distribution_count"], 12)
        self.assertEqual(result["minus_four_allowed_absolute_values"], [0, 1])
        self.assertEqual(
            result["minus_four_survivors"],
            [{"-1": 7, "0": 85, "1": 7}],
        )

    def test_minus_three_hostile_mutation(self) -> None:
        result = check.amplitude_screen()
        self.assertEqual(result["minus_three_allowed_absolute_values"], [0, 1, 2])
        self.assertEqual(result["minus_three_survivor_count"], 3)
        self.assertEqual(
            result["minus_three_hostile_witness"],
            {"-1": 6, "0": 88, "1": 4, "2": 1},
        )

    def test_independent_root_pattern_census(self) -> None:
        result = check.root_pattern_census()
        self.assertEqual(
            result["counts"],
            {
                "moment_only": 46,
                "tensor_energy": 32,
                "extreme_fiber": 16,
                "no_extreme_coordinates": 1,
            },
        )
        self.assertEqual(
            result["final_pattern"],
            {
                "plus_2": 0,
                "plus_1": 21,
                "zero": 189,
                "minus_1": 21,
                "minus_2": 0,
                "cube_sum": 0,
            },
        )

    def test_extreme_fiber_psd_census(self) -> None:
        result = check.extreme_fiber_census()
        self.assertEqual(result["psd_counts"], {"1": 1, "2": 2, "3": 1, "4": 0})
        self.assertFalse(result["size_four_survives"])
        self.assertEqual(
            result["size_three_gram"],
            [[2, -1, -1], [-1, 2, -1], [-1, -1, 2]],
        )

    def test_relaxed_extreme_alphabet_is_active(self) -> None:
        result = check.extreme_fiber_census((-2, -1, 0))
        self.assertTrue(result["size_four_survives"])

    def test_support_design_forcing(self) -> None:
        result = check.design_forcing()
        self.assertEqual(result["passing_same_sign_edge_counts"], [0])
        self.assertEqual(result["row_sums"], [4] * 7)
        self.assertEqual(result["column_sums"], [4] * 7)
        self.assertEqual(result["same_side_intersections"], [2])

    def test_mu_three_count_mutation(self) -> None:
        result = check.design_forcing(3)
        self.assertEqual(result["passing_same_sign_edge_counts"], [0, 1, 2])

    def test_outside_and_triangle_census(self) -> None:
        result = check.outside_triangle_census()
        self.assertEqual(
            result["outside_types"],
            {
                "support_edge_completion": 28,
                "support_nonedge_completion": 42,
                "no_support_neighbor": 15,
            },
        )
        self.assertEqual(
            result["root_triangle_pattern"],
            {"plus_1": 21, "zero": 189, "minus_1": 21},
        )
        self.assertEqual(sum(result["triangle_types"].values()), 231)

    def test_partial_control_main_checks(self) -> None:
        result = check.hostile_partial_control()
        self.assertEqual(result["status"], "PARTIAL_LOCAL_CONTROL_NOT_EXTENDIBILITY_EVIDENCE")
        self.assertEqual(result["vertex_count"], 99)
        self.assertEqual(result["edge_count"], 210)
        self.assertEqual(
            result["current_degree_histogram"],
            {"0": 15, "2": 28, "4": 42, "14": 14},
        )
        self.assertEqual(
            result["support_pair_common_neighbors"],
            {"edge": [1], "nonedge": [2]},
        )

    def test_partial_control_degree_correction(self) -> None:
        result = check.hostile_partial_control()
        self.assertEqual(
            result["correct_remaining_degrees"],
            {
                "support_edge_completion": 12,
                "support_nonedge_completion": 10,
                "no_support_neighbor": 14,
            },
        )
        self.assertEqual(result["candidate_v1_correction"], [10, 12, 14])
        self.assertEqual(
            result["discovery_v2_remaining_degree_distribution"],
            {"10": 42, "12": 28, "14": 15},
        )
        self.assertNotEqual(
            result["candidate_v1_stated_remaining_degrees"],
            result["candidate_v1_correction"],
        )

    def test_tensor_schur_and_A4_constants(self) -> None:
        result = check.tensor_schur_constraints()
        self.assertEqual(result["minimum_trace_lift_norm_factor"], "1/15")
        self.assertEqual(result["H2_mod_4"], 2)
        self.assertEqual(
            result["possible_g2"],
            [6, 14, 22, 30, 38, 46, 54, 62, 70, 78],
        )
        self.assertEqual(result["corresponding_f"], list(range(141, 131, -1)))
        self.assertEqual(
            result["incidence_constants"],
            {
                "norm_Np_squared": 294,
                "sum_Np": 126,
                "fixed_Np_A_Np": 1512,
                "g2_formula": "1134-8f",
            },
        )

    def test_reflection_coefficients_and_scope_witness(self) -> None:
        result = check.reflection_constraints()
        self.assertEqual(result["coordinate_involution_error"], "0")
        self.assertNotEqual(result["hostile_denominator_42_error"], "0")
        self.assertEqual(result["vertex_involution_error"], "0")
        self.assertIn("1/21", result["not_coordinate_permutation_witness"])

    def test_status_wall(self) -> None:
        result = check.build_results()
        statuses = {row["id"]: row["status"] for row in result["obligations"]}
        self.assertEqual(
            statuses["candidate_v1_partial_control_remaining_degree_text"],
            "FAIL",
        )
        self.assertEqual(statuses["discovery_v2_manifest_replay"], "PASS")
        self.assertEqual(
            statuses["discovery_v2_partial_control_remaining_degrees"],
            "PASS",
        )
        self.assertEqual(statuses["root_exclusion"], "UNKNOWN")
        self.assertEqual(statuses["rooted_endpoint"], "UNKNOWN")
        self.assertEqual(statuses["Conway_99"], "UNKNOWN")

    def test_deterministic_lf_json(self) -> None:
        encoded = check.canonical_json(check.build_results())
        parsed = json.loads(encoded)
        self.assertEqual(parsed["schema_version"], 1)
        self.assertNotIn(b"\r\n", encoded)
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "results.json"
            target.write_bytes(encoded)
            observed = target.read_bytes()
        self.assertEqual(observed, encoded)
        self.assertEqual(
            hashlib.sha256(observed).hexdigest(),
            hashlib.sha256(encoded).hexdigest(),
        )


if __name__ == "__main__":
    unittest.main()
