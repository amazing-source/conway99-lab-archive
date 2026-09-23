from __future__ import annotations

import json
import tempfile
import unittest
from fractions import Fraction
from pathlib import Path

import independent_check as check


class Wave28IndependentCheckTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.base = check.reconstruct_wave27()
        cls.results = check.build_results()
        cls.preferred = cls.results["supports"]["preferred_all_six_blocks"]
        cls.initial = cls.results["supports"]["initial_index_32_cross_control"]
        cls.checked_path = Path(__file__).with_name("independent-results.json")

    def test_01_frozen_input_hashes(self) -> None:
        self.assertEqual(
            {
                path: metadata["sha256"]
                for path, metadata in self.results["inputs"].items()
            },
            check.EXPECTED_INPUT_HASHES,
        )

    def test_02_wave27_reconstruction_is_not_an_import(self) -> None:
        self.assertEqual(check.determinant(self.base["E8"]), 1)
        self.assertEqual(check.determinant(self.base["E6"]), 3)
        self.assertEqual(check.determinant(self.base["S"]), 9)
        self.assertEqual(check.determinant(self.base["Q"]), 9)
        self.assertEqual(check.trace(self.base["B"]), 60)

    def test_03_preferred_support_meets_all_six_blocks(self) -> None:
        support = set(self.preferred["support"])
        for start, block in zip(self.base["starts"], self.base["blocks_s"]):
            self.assertTrue(any(start <= value < start + len(block) for value in support))

    def test_04_chronology_and_exact_supports(self) -> None:
        self.assertEqual(tuple(self.preferred["support"]), check.PREFERRED_SUPPORT)
        self.assertEqual(tuple(self.initial["support"]), check.INITIAL_SUPPORT)
        self.assertEqual(self.preferred["name"], "preferred_all_six_blocks")
        self.assertEqual(self.initial["name"], "initial_index_32_cross_control")

    def test_05_neighbor_bases_are_unimodular_rational_bases(self) -> None:
        for support in (self.preferred, self.initial):
            self.assertEqual(abs(support["basis"]["det_P"]), 1)
            self.assertEqual(abs(support["basis"]["det_H_basis"]), 2)
            self.assertTrue(support["basis"]["inverse_reconstructed_by_fraction_gauss_jordan"])

    def test_06_simultaneous_neighbor_norms(self) -> None:
        expected = {"v_S_v": 16, "a_Q_a": 16, "a_G_a": 336}
        self.assertEqual(self.preferred["simultaneous_neighbor_norms"], expected)
        self.assertEqual(self.initial["simultaneous_neighbor_norms"], expected)

    def test_07_transformed_form_invariants(self) -> None:
        for support in (self.preferred, self.initial):
            invariants = support["invariants"]
            self.assertTrue(invariants["S_even_integral_symmetric_pd"])
            self.assertTrue(invariants["Q_even_integral_symmetric_pd"])
            self.assertTrue(invariants["G_even_integral_symmetric_pd"])
            self.assertTrue(invariants["SG_equals_21I"])
            self.assertEqual(invariants["det_S"], 9)
            self.assertEqual(invariants["det_Q"], 9)
            self.assertEqual(invariants["det_B"], 81)
            self.assertEqual(invariants["trace_B"], 60)

    def test_08_direct_B_parity_and_C_square_trace(self) -> None:
        for support in (self.preferred, self.initial):
            invariants = support["invariants"]
            self.assertTrue(invariants["B_identity_mod_2"])
            self.assertTrue(invariants["C_integral"])
            self.assertEqual(invariants["trace_C"], 8)
            self.assertEqual(invariants["trace_C_squared"], 32)
            self.assertTrue(invariants["C_squared_equals_4C"])

    def test_09_complete_matrix_shapes_and_hashes(self) -> None:
        expected_keys = {"S_prime", "Q_prime", "G_prime", "B_prime", "C_prime"}
        for support in (self.preferred, self.initial):
            self.assertEqual(set(support["matrices"]), expected_keys)
            self.assertEqual(set(support["matrix_hashes"]), expected_keys)
            for key in expected_keys:
                matrix = support["matrices"][key]
                self.assertEqual(len(matrix), 44)
                self.assertTrue(all(len(row) == 44 for row in matrix))
                self.assertEqual(
                    check.canonical_hash(matrix), support["matrix_hashes"][key]
                )

    def test_10_preferred_complete_root_census(self) -> None:
        roots = self.preferred["roots"]
        self.assertEqual(roots["H_coset"]["root_count"], 568)
        self.assertEqual(roots["half_coset"]["new_roots_in_v_over_2_plus_H"], 0)
        self.assertTrue(roots["half_coset"]["complete"])
        self.assertTrue(roots["half_coset"]["no_arbitrary_coordinate_box"])
        self.assertEqual(roots["total_root_count"], 568)

    def test_11_preferred_rank_and_components(self) -> None:
        roots = self.preferred["roots"]
        self.assertEqual(roots["root_span_rank"], 43)
        self.assertEqual(
            roots["component_sizes"],
            [2, 2, 2, 2, 30, 40, 112, 126, 126, 126],
        )
        self.assertEqual(
            roots["component_types"],
            ["A1", "A1", "A1", "A1", "A5", "D5", "D8", "E7", "E7", "E7"],
        )
        self.assertFalse(roots["root_lattice"]["full_rank"])

    def test_12_preferred_evades_named_component_screens_only_abstractly(self) -> None:
        types = set(self.preferred["roots"]["component_types"])
        self.assertTrue(types.isdisjoint({"A2", "A6", "E6", "A20"}))
        wall = self.results["status_wall"]
        self.assertEqual(wall["projector_frame"], "NOT_CONSTRUCTED")
        self.assertEqual(wall["Schur_square_origin"], "NOT_CONSTRUCTED")

    def test_13_initial_complete_root_census(self) -> None:
        roots = self.initial["roots"]
        self.assertEqual(roots["H_coset"]["root_count"], 568)
        self.assertEqual(roots["half_coset"]["new_roots_in_v_over_2_plus_H"], 0)
        self.assertTrue(roots["half_coset"]["complete"])
        self.assertEqual(roots["root_span_rank"], 44)

    def test_14_preferred_rank_one_glue_dictionary(self) -> None:
        glue = self.preferred["preferred_glue_dictionary"]
        self.assertEqual(
            glue["z_original_coordinates"],
            list(check.PREFERRED_ORTHOGONAL_LINE),
        )
        self.assertTrue(glue["z_primitive_in_L_prime"])
        self.assertEqual(glue["z_norm"], 12)
        self.assertEqual(glue["z_divisibility_in_L_prime"], 3)
        self.assertEqual(glue["K"]["rank"], 1)
        self.assertEqual(glue["K"]["determinant"], 12)
        self.assertTrue(glue["K"]["rootless"])

    def test_15_preferred_H0_H1_indices(self) -> None:
        glue = self.preferred["preferred_glue_dictionary"]
        self.assertEqual(glue["R"]["rank"], 43)
        self.assertEqual(glue["R"]["determinant"], 12288)
        self.assertEqual(glue["Rbar"]["rank"], 43)
        self.assertEqual(glue["Rbar"]["determinant"], 12)
        self.assertTrue(glue["Rbar"]["saturated_exact_kernel"])
        self.assertEqual(glue["H0_order_Rbar_over_R"], 32)
        self.assertEqual(glue["H1_order_L_over_Rbar_plus_K"], 4)
        self.assertEqual(glue["total_index_L_over_K_plus_R"], 128)
        self.assertEqual(glue["determinant_identity"]["evaluated"], 9)

    def test_16_initial_component_profile(self) -> None:
        roots = self.initial["roots"]
        self.assertEqual(
            roots["component_sizes"], [2, 2, 30, 72, 112, 112, 112, 126]
        )
        self.assertEqual(
            roots["component_types"],
            ["A1", "A1", "A5", "D8", "D8", "D8", "E6", "E7"],
        )

    def test_17_initial_glue_index_and_determinant(self) -> None:
        root_lattice = self.initial["roots"]["root_lattice"]
        self.assertTrue(root_lattice["full_rank"])
        self.assertEqual(root_lattice["index_in_neighbor_lattice"], 32)
        self.assertEqual(root_lattice["determinant_if_full_rank"], 9216)
        self.assertEqual(9 * 32 * 32, 9216)

    def test_18_component_types_come_from_checked_cartan_data(self) -> None:
        for support in (self.preferred, self.initial):
            for component in support["roots"]["components"]:
                cartan = [
                    [Fraction(value) for value in row]
                    for row in component["cartan_matrix"]
                ]
                classified, arms = check.classify_cartan(cartan)
                self.assertEqual(classified, component["type"])
                self.assertEqual(arms, component["dynkin_arm_lengths"])
                self.assertEqual(check.matrix_rank(cartan), component["rank"])
                self.assertEqual(
                    check.determinant(cartan), component["cartan_determinant"]
                )
                self.assertTrue(
                    component["all_roots_integrally_generated_by_simple_roots"]
                )

    def test_19_block_enumerations_have_proved_exact_bounds(self) -> None:
        for support in (self.preferred, self.initial):
            half = support["roots"]["half_coset"]
            self.assertIn("q(v/2+x)=2 iff q(v+2x)=8", half["norm_conversion"])
            for block in half["blocks"]:
                enumeration = block["enumeration"]
                self.assertEqual(enumeration["cap"], 8)
                self.assertEqual(enumeration["modulus"], 2)
                self.assertIn("integer isqrt", enumeration["bound_method"])

    def test_20_direct_44d_timeout_is_non_evidence(self) -> None:
        timeout = self.results["direct_44d_timeout"]
        self.assertEqual(timeout["reported_elapsed_seconds"], 124)
        self.assertFalse(timeout["replayed"])
        self.assertFalse(timeout["evidentiary"])

    def test_21_status_wall(self) -> None:
        wall = self.results["status_wall"]
        self.assertEqual(wall["scoped_hostile_controls"], "VERIFIED_BY_THIS_INDEPENDENT_CHECK")
        self.assertEqual(wall["primitive_Z231_embedding"], "NOT_CONSTRUCTED")
        self.assertEqual(wall["required_M_entry_alphabet_and_profiles"], "NOT_CONSTRUCTED")
        self.assertEqual(wall["graph"], "NOT_CONSTRUCTED")
        self.assertEqual(wall["n3_708"], "UNKNOWN")
        self.assertEqual(wall["Conway_99"], "UNKNOWN")
        self.assertEqual(wall["novelty"], "UNKNOWN")

    def test_22_support_mutation_breaks_simultaneous_norms(self) -> None:
        mutated = tuple(
            sorted((set(check.PREFERRED_SUPPORT) - {41}) | {2})
        )
        neighbor = check.construct_neighbor_basis(self.base["S"], mutated)
        v = neighbor["v"]
        a = neighbor["a"]
        observed = (
            check.quadratic(v, self.base["S"]),
            check.quadratic(a, self.base["Q"]),
            check.quadratic(a, self.base["G"]),
        )
        self.assertNotEqual(observed, (16, 16, 336))

    def test_23_norm_preserving_mutation_is_not_misreported(self) -> None:
        # The first hostile-test draft incorrectly assumed 41 -> 42 would
        # break the three scalar norms.  It does not; retain that fact and
        # avoid converting the failed test design into negative evidence.
        mutated = tuple(
            sorted((set(check.PREFERRED_SUPPORT) - {41}) | {42})
        )
        neighbor = check.construct_neighbor_basis(self.base["S"], mutated)
        v = neighbor["v"]
        a = neighbor["a"]
        observed = (
            check.quadratic(v, self.base["S"]),
            check.quadratic(a, self.base["Q"]),
            check.quadratic(a, self.base["G"]),
        )
        self.assertEqual(observed, (16, 16, 336))

    def test_24_basis_corruption_is_detected(self) -> None:
        neighbor = check.construct_neighbor_basis(self.base["S"], check.PREFERRED_SUPPORT)
        corrupted = [row[:] for row in neighbor["P"]]
        corrupted[0][0] += Fraction(1, 2)
        self.assertNotEqual(abs(check.determinant(corrupted)), 1)

    def test_25_checked_result_is_byte_reproducible(self) -> None:
        checked = json.loads(self.checked_path.read_text(encoding="utf-8"))
        self.assertEqual(checked, self.results)
        with tempfile.TemporaryDirectory() as temp_dir:
            regenerated = Path(temp_dir) / "independent-results.json"
            check.write_results(regenerated, self.results)
            self.assertEqual(regenerated.read_bytes(), self.checked_path.read_bytes())


if __name__ == "__main__":
    unittest.main()
