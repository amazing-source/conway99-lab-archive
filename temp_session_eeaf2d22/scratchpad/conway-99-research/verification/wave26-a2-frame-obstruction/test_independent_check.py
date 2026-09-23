import json
import tempfile
import unittest
from pathlib import Path

import independent_check as check


class A2FrameObstructionTests(unittest.TestCase):
    def test_frozen_public_inputs(self):
        self.assertEqual(check.verify_frozen_inputs(), dict(sorted(check.EXPECTED_INPUTS.items())))

    def test_basis_invariant_factorization(self):
        result = check.basis_invariance_toy_check()
        self.assertTrue(result["original_gram_is_21_s_inverse"])
        self.assertTrue(result["M_factorization_preserved"])
        self.assertTrue(result["transformed_frame_identity"])

    def test_a2_has_six_oriented_roots(self):
        roots = check.enumerate_a2_roots()
        self.assertEqual(len(roots), 6)
        self.assertEqual(
            set(roots),
            {(-1, -1), (-1, 0), (0, -1), (0, 1), (1, 0), (1, 1)},
        )

    def test_a2_has_no_norm_four(self):
        result = check.a2_norm_four_residue_obstruction()
        self.assertEqual(result["represented_residues"], [0, 1])
        self.assertFalse(result["has_norm_four"])

    def test_frame_identity_forces_energy_42(self):
        result = check.frame_energy_data()
        self.assertEqual(result["coordinate_second_moment"], [[14, 7], [7, 14]])
        self.assertEqual(result["a2_energy"], 42)
        self.assertEqual(result["root_rows_forced"], 21)

    def test_original_alphabet_forces_fiber_cap_three(self):
        result = check.same_oriented_root_fiber_data()
        self.assertEqual(result["cauchy_feasible_residual_inner_products"], [-2, -1])
        self.assertEqual(result["four_vector_sum_norm_upper"], -4)
        self.assertEqual(result["fiber_cap"], 3)

    def test_three_in_one_fiber_is_not_overexcluded(self):
        result = check.shared_root_edge_cases()
        triple = result["three_same_oriented_roots_are_locally_possible"]
        self.assertEqual(triple["total_off_diagonals"], [1])
        self.assertTrue(triple["passes_original_set"])

    def test_opposite_orientations_are_distinct_fibers(self):
        result = check.shared_root_edge_cases()
        opposite = result["opposite_orientations_must_be_separate_fibers"]
        self.assertEqual(opposite["a2_inner"], -2)
        self.assertEqual(opposite["total_inner"], 0)
        self.assertTrue(opposite["passes_original_set"])

    def test_pigeonhole_contradiction(self):
        result = check.build_result()
        self.assertEqual(result["frame_count"]["root_rows_forced"], 21)
        self.assertEqual(result["frame_count"]["total_root_capacity"], 18)
        self.assertTrue(result["frame_count"]["forced_root_rows_exceed_capacity"])

    def test_plus_two_hostile_control_breaks_cap(self):
        result = check.plus_two_hostile_relaxation()
        self.assertEqual(result["row_count_same_oriented_root"], 4)
        self.assertEqual(result["off_diagonals"], [2])
        self.assertTrue(result["accepted_if_plus_two_added"])
        self.assertFalse(result["accepted_originally"])
        weakened = check.same_oriented_root_fiber_data(
            check.ORIGINAL_OFF_DIAGONALS + (2,)
        )
        self.assertIsNone(weakened["fiber_cap"])

    def test_missing_frame_hostile_control(self):
        result = check.missing_frame_hostile_relaxation()
        self.assertTrue(result["local_projector_row_conditions_pass"])
        self.assertEqual(result["actual_a2_energy"], 0)
        self.assertEqual(result["required_a2_energy"], 42)
        self.assertFalse(result["frame_identity_pass"])

    def test_wave24_survivor_has_exact_a2_blocks(self):
        result = check.survivor_check()
        self.assertEqual(result["rank"], 44)
        self.assertEqual(result["det_A2"], 3)
        self.assertEqual(result["det_E8"], 1)
        self.assertTrue(result["S_is_exact_E8_5_orthogonal_A2_2"])
        self.assertTrue(result["projector_frame_realization_excluded"])

    def test_scope_does_not_inflate(self):
        scope = check.build_result()["scope"]
        self.assertEqual(scope["exact_E8_5_orthogonal_A2_2_projector_frame"], "EXCLUDED")
        self.assertEqual(scope["abstract_E8_5_orthogonal_A2_2_coordinate_lattice"], "PRESERVED")
        self.assertEqual(scope["arbitrary_primitive_embedding_without_projector_frame"], "UNKNOWN")
        self.assertEqual(scope["all_h_equals_9_forms"], "UNKNOWN")
        self.assertEqual(scope["n3_equals_708"], "NOT_EXCLUDED")
        self.assertEqual(scope["conway_99"], "UNKNOWN")

    def test_json_is_deterministic_and_lf_terminated(self):
        result = check.build_result()
        expected = json.dumps(result, indent=2, sort_keys=True) + "\n"
        with tempfile.TemporaryDirectory() as directory:
            first = Path(directory) / "first.json"
            second = Path(directory) / "second.json"
            for output in (first, second):
                rendered = json.dumps(check.build_result(), indent=2, sort_keys=True) + "\n"
                output.write_text(rendered, encoding="utf-8", newline="\n")
            self.assertEqual(first.read_bytes(), second.read_bytes())
            self.assertEqual(first.read_text(encoding="utf-8"), expected)
            self.assertTrue(first.read_bytes().endswith(b"\n"))
            self.assertNotIn(b"\r\n", first.read_bytes())


if __name__ == "__main__":
    unittest.main()
