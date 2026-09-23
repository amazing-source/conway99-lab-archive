from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from fractions import Fraction
from pathlib import Path

import exact_check as ec


class Wave26A2FrameObstructionChecks(unittest.TestCase):
    def test_public_base_and_frozen_inputs(self) -> None:
        self.assertEqual(
            ec.PUBLIC_BASE_COMMIT,
            "1f22323a2805e3e24f7848d53f2f4813e236fae9",
        )
        self.assertEqual(len(ec.INPUTS), 4)
        for path, expected in ec.INPUTS.items():
            self.assertEqual(ec.sha256(ec.ROOT / path), expected)

    def test_frozen_survivor_has_two_orthogonal_A2_blocks(self) -> None:
        data = ec.frozen_survivor_structure()
        self.assertEqual(data["rank"], 44)
        self.assertEqual(data["A2_block_starts_zero_based"], [40, 42])
        self.assertEqual(data["orthogonal_A2_block_count"], 2)

    def test_A2_root_enumeration_is_exact(self) -> None:
        data = ec.a2_representation_certificate()
        self.assertEqual(data["oriented_root_count"], 6)
        self.assertEqual(
            data["norm_two_vectors"],
            [
                [-1, -1],
                [-1, 0],
                [0, -1],
                [0, 1],
                [1, 0],
                [1, 1],
            ],
        )
        self.assertEqual(data["norm_four_vectors"], [])

    def test_A2_norm_four_mod_three_obstruction(self) -> None:
        data = ec.a2_representation_certificate()
        self.assertTrue(data["norm_four_absent_mod_3"])
        self.assertEqual(
            data["mod_3_values_of_a2_minus_ab_plus_b2"],
            [0, 1],
        )
        for a in range(-8, 9):
            for b in range(-8, 9):
                self.assertNotEqual(a * a - a * b + b * b, 2)

    def test_basis_invariance_and_contragredient_change(self) -> None:
        data = ec.basis_invariance_certificate()
        change = data["basis_change"]
        self.assertEqual(change["Y_dimensions"], [21, 2])
        self.assertEqual(
            change["lattice_basis_matrix_A_equals_P_inverse_transpose"],
            [[1, 0], [-1, 1]],
        )
        self.assertTrue(change["M_unchanged"])
        self.assertTrue(change["second_moment_covariant"])

    def test_block_energy_forces_twenty_one_rows(self) -> None:
        data = ec.frame_obstruction_certificate()
        self.assertEqual(data["A2_block_energy"], 42)
        self.assertEqual(data["forced_A2_incident_rows"], 21)
        self.assertEqual(
            data["possible_A2_component_norms_for_a_norm_four_row"],
            [0, 2],
        )

    def test_same_root_fiber_inner_products(self) -> None:
        data = ec.frame_obstruction_certificate()
        self.assertEqual(
            data["actual_projector_off_diagonals"],
            [-2, -1, 0, 1],
        )
        self.assertEqual(
            data["same_root_fiber_complement_inner_products"],
            [-2, -1],
        )

    def test_fiber_capacity_is_three(self) -> None:
        data = ec.frame_obstruction_certificate()
        bounds = data["fiber_sum_norm_upper_bounds"]
        self.assertEqual(bounds[3], 0)
        self.assertEqual(bounds[4], -4)
        self.assertEqual(data["fiber_capacity_per_oriented_root"], 3)

    def test_total_capacity_eighteen_contradicts_twenty_one(self) -> None:
        data = ec.frame_obstruction_certificate()
        self.assertEqual(data["oriented_A2_root_count"], 6)
        self.assertEqual(data["total_A2_incident_row_capacity"], 18)
        self.assertEqual(data["contradiction_gap"], 3)
        self.assertTrue(data["contradiction"])

    def test_row_meeting_both_A2_blocks_is_covered(self) -> None:
        data = ec.shared_a2_row_certificate()
        self.assertEqual(data["full_row_norm"], 4)
        self.assertEqual(data["first_A2_component_norm"], 2)
        self.assertEqual(data["second_A2_component_norm"], 2)
        self.assertIn("counted once in each", data["counting_rule"])

    def test_allow_plus_two_hostile_control(self) -> None:
        data = ec.plus_two_hostile_control()
        self.assertEqual(data["fiber_size"], 4)
        self.assertEqual(data["diagonal"], [4, 4, 4, 4])
        self.assertEqual(data["off_diagonal_values"], [2])
        self.assertTrue(data["valid_if_plus_two_is_allowed"])
        self.assertFalse(data["valid_for_actual_off_diagonals"])

    def test_omitted_frame_identity_hostile_control(self) -> None:
        data = ec.omitted_frame_identity_control()
        self.assertEqual(data["row_count"], 18)
        self.assertTrue(data["all_local_row_constraints_hold"])
        self.assertEqual(data["off_diagonal_values"], [-2, -1, 1])
        self.assertEqual(
            data["central_A2_second_moment"],
            [[12, 6], [6, 12]],
        )
        self.assertEqual(
            data["required_frame_second_moment"],
            [[14, 7], [7, 14]],
        )
        self.assertFalse(data["frame_identity_holds_on_central_A2"])
        self.assertEqual(data["central_A2_energy"], 36)

    def test_scope_walls(self) -> None:
        conclusion = ec.build_results()["conclusion"]
        self.assertEqual(
            conclusion["wave24_exact_survivor_projector_origin"],
            "REFUTED",
        )
        self.assertEqual(
            conclusion["wave24_exact_survivor_arbitrary_primitive_embedding"],
            "UNKNOWN",
        )
        self.assertFalse(conclusion["all_h9_lattices_excluded"])
        self.assertFalse(conclusion["h9_arithmetic_row_excluded"])
        self.assertFalse(conclusion["n3_708_excluded"])
        self.assertEqual(conclusion["target_status"], "UNKNOWN")
        self.assertEqual(conclusion["novelty_status"], "UNKNOWN")

    def test_deterministic_lf_json(self) -> None:
        payload = ec.build_results()
        expected = (
            json.dumps(payload, indent=2, sort_keys=True) + "\n"
        ).encode("utf-8")
        self.assertNotIn(b"\r\n", expected)
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "result.json"
            output.write_bytes(expected)
            self.assertEqual(
                hashlib.sha256(output.read_bytes()).hexdigest(),
                hashlib.sha256(expected).hexdigest(),
            )

    def test_exact_inverse_control(self) -> None:
        inverse = ec.inverse(ec.A2)
        self.assertEqual(
            inverse,
            [
                [Fraction(2, 3), Fraction(1, 3)],
                [Fraction(1, 3), Fraction(2, 3)],
            ],
        )
        self.assertEqual(
            ec.matmul(ec.A2, inverse),
            [[Fraction(1), Fraction(0)], [Fraction(0), Fraction(1)]],
        )


if __name__ == "__main__":
    unittest.main()
