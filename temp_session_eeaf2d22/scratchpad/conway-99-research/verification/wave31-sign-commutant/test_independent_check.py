from __future__ import annotations

import tempfile
import unittest
from fractions import Fraction
from pathlib import Path

import independent_check as check


class IndependentWave31VerifierTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = check.derive()

    def test_target_spectrum_and_incidence_counts(self) -> None:
        target = self.result["target"]
        self.assertEqual(target["adjacency_eigenvalues"], [14, 3, -4])
        self.assertEqual(target["adjacency_multiplicities"], [1, 54, 44])
        self.assertEqual(target["triangles"], 231)
        self.assertEqual(target["triangles_per_vertex"], 7)
        self.assertEqual(target["gamma_eigenvalues"], [18, 7, 0, -3])
        self.assertEqual(target["gamma_multiplicities"], [1, 54, 44, 132])

    def test_projector_formula_on_all_eigenspaces(self) -> None:
        projector = self.result["projector"]
        self.assertEqual(projector["integer_formula"], "(27I-9A+J)/63")
        self.assertEqual(
            projector["eigenspace_values"],
            {"14": 0, "3": 0, "-4": 1},
        )

    def test_incidence_transport_is_scaled_bijection(self) -> None:
        transport = self.result["incidence_transport"]
        self.assertEqual(transport["norm_square_scale"], 3)
        self.assertTrue(transport["injective"])
        self.assertEqual(transport["transported_adjacency_eigenvalue"], -4)
        self.assertEqual(transport["domain_dimension"], 44)
        self.assertEqual(transport["target_dimension"], 44)
        self.assertTrue(transport["onto_minus_four_eigenspace"])

    def test_rootless_norm_four_support(self) -> None:
        support = self.result["rootless_block_support"]
        for patterns in support["norm_four_patterns"].values():
            for pattern in patterns:
                self.assertEqual(sum(pattern), 4)
                self.assertEqual(sum(value != 0 for value in pattern), 1)
        self.assertEqual(support["rooted_counterpattern"], [2, 2])
        self.assertEqual(
            support["evenness_role"],
            "inherited endpoint hypothesis but unnecessary for one-block row support",
        )

    def test_DE_commutation_is_active(self) -> None:
        control = self.result["transport_commutation"]["drop_DE_equals_ED"]
        self.assertFalse(control["commutes"])
        self.assertFalse(control["D_preserves_imE"])

    def test_symmetry_is_active(self) -> None:
        transport = self.result["transport_commutation"]
        self.assertTrue(transport["symmetric_preserver_commutes"])
        self.assertGreater(transport["symmetric_preserver_examples_checked"], 0)
        self.assertTrue(transport["nonsymmetric_preserver"]["preserves_V"])
        self.assertFalse(transport["nonsymmetric_preserver"]["commutes_with_P"])

    def test_commutator_sign_and_coefficients(self) -> None:
        commutator = self.result["commutator"]
        self.assertEqual(commutator["projector_commutator"], "9(KA-AK)=KJ-JK")
        self.assertEqual(
            commutator["coefficients"],
            {"projector_A": 9, "K_one": 3, "reduced": 3},
        )
        self.assertEqual(
            commutator["reduced_identity"],
            "3(KA-AK)=d1^T-1d^T",
        )
        self.assertTrue(commutator["generic_matrix_sign_check"])

    def test_all_adjacent_summands_are_partitioned(self) -> None:
        local = self.result["adjacent_local_audit"]["shared_triangle_sign"]
        self.assertEqual(local["summands_checked"], 99)
        self.assertEqual(
            sum(item["count"] for item in local["categories"]),
            99,
        )
        self.assertEqual(local["ZA_xy"], 1)
        self.assertEqual(local["AZ_xy"], 1)
        self.assertEqual(local["ZA_minus_AZ_xy"], 0)
        self.assertTrue(local["cancels"])

    def test_shared_sign_comes_from_same_unique_triangle(self) -> None:
        local = self.result["adjacent_local_audit"]
        self.assertEqual(local["adjacent_equation_shared"], "3(d_x-d_y)=d_x-d_y")
        self.assertEqual(local["shared_consequence"], "d_x=d_y")

    def test_mutated_edge_signs_break_cancellation(self) -> None:
        local = self.result["adjacent_local_audit"]
        mutated = local["mutated_edge_signs"]
        self.assertEqual(mutated["ZA_xy"], 1)
        self.assertEqual(mutated["AZ_xy"], -1)
        self.assertEqual(mutated["ZA_minus_AZ_xy"], 2)
        self.assertFalse(mutated["cancels"])
        self.assertEqual(local["mutation_permitted_difference"], -3)

    def test_target_is_connected_without_extra_assumption(self) -> None:
        connectivity = self.result["connectedness"]
        self.assertEqual(connectivity["nonadjacent_common_neighbors"], 2)
        self.assertTrue(connectivity["connected"])
        self.assertEqual(connectivity["diameter_at_most"], 2)

    def test_double_count_sizes(self) -> None:
        sizes = self.result["divisibility_and_trace"]["constant_degree_size_census"]
        self.assertEqual([item["block_size"] for item in sizes], list(range(0, 232, 33)))
        self.assertEqual(
            [item["constant_signed_degree"] for item in sizes],
            list(range(-7, 8, 2)),
        )
        self.assertTrue(all(item["block_size_mod_33"] == 0 for item in sizes))

    def test_trace_identity_excludes_every_proper_rank(self) -> None:
        census = self.result["divisibility_and_trace"]["proper_rank_census"]
        self.assertEqual([item["rank"] for item in census], list(range(4, 44, 4)))
        self.assertEqual([item["rows"] for item in census], list(range(21, 211, 21)))
        self.assertTrue(all(item["excluded"] for item in census))
        self.assertTrue(all(item["rows_mod_33"] != 0 for item in census))

    def test_coordinate_projector_trace_gives_same_21_divisibility(self) -> None:
        arithmetic = self.result["divisibility_and_trace"]
        self.assertEqual(
            arithmetic["coordinate_projector_trace"],
            "rank(E_I)=tr(E_I)=4b/21",
        )
        self.assertEqual(
            arithmetic["coordinate_projector_trace_consequence"],
            "21 divides b",
        )
        self.assertEqual(
            [item["block_rows"] for item in arithmetic["coordinate_projector_rank_census"]],
            list(range(0, 232, 21)),
        )

    def test_lcm_short_form_excludes_proper_block(self) -> None:
        arithmetic = self.result["divisibility_and_trace"]
        self.assertEqual(arithmetic["combined_row_divisibility"], "lcm(21,33)=231 divides b")
        self.assertEqual(arithmetic["proper_block_range"], "0<b<231")

    def test_wave30_both_block_sizes_fail(self) -> None:
        arithmetic = self.result["divisibility_and_trace"]
        self.assertEqual(arithmetic["wave30_rows"], {"rank20": 105, "rank24": 126})
        self.assertEqual(arithmetic["wave30_rows_mod_33"], {"rank20": 6, "rank24": 27})

    def test_full_and_empty_controls_are_not_excluded(self) -> None:
        sizes = self.result["divisibility_and_trace"]["constant_degree_size_census"]
        self.assertIn(
            {"constant_signed_degree": -7, "block_size": 0, "block_size_mod_33": 0},
            sizes,
        )
        self.assertIn(
            {"constant_signed_degree": 7, "block_size": 231, "block_size_mod_33": 0},
            sizes,
        )
        self.assertEqual(21 * 44 // 4, 231)

    def test_every_named_premise_fails_closed(self) -> None:
        for premise in check.ESSENTIAL_PREMISES:
            enabled = set(check.ESSENTIAL_PREMISES)
            enabled.remove(premise)
            with self.subTest(premise=premise):
                with self.assertRaises(check.PremiseError):
                    check.derive(enabled)

    def test_hostile_countermodels_are_retained(self) -> None:
        controls = self.result["hostile_controls"]
        self.assertEqual(controls["drop_rootlessness"]["counterpattern"], [2, 2])
        self.assertEqual(
            controls["drop_nonzero_component_norm_floor"]["counterpattern"],
            [1, 3],
        )
        self.assertIn("no failure", controls["drop_evenness_alone"]["effect"])
        self.assertEqual(controls["drop_shared_triangle_sign"]["ZA_minus_AZ_xy"], 2)
        self.assertEqual(
            controls["drop_shared_triangle_sign"]["permitted_d_x_minus_d_y"],
            -3,
        )

    def test_scope_wall(self) -> None:
        scope = self.result["scope"]
        self.assertEqual(
            scope["rootless_decomposable_endpoint_forms"],
            "REFUTED_VERIFIED_SCOPED",
        )
        self.assertEqual(scope["rootless_indecomposable_endpoint_forms"], "UNKNOWN")
        self.assertEqual(scope["rooted_endpoint_forms"], "UNKNOWN")
        self.assertEqual(scope["n3_708"], "UNKNOWN")
        self.assertEqual(scope["Conway_99"], "UNKNOWN")
        self.assertEqual(scope["novelty"], "UNKNOWN")

    def test_deterministic_lf_json(self) -> None:
        candidate = Path(__file__).with_name("independent-results.json")
        with tempfile.TemporaryDirectory() as directory:
            generated = Path(directory) / "independent-results.json"
            check.write_json(generated, self.result)
            self.assertEqual(generated.read_bytes(), candidate.read_bytes())
            self.assertTrue(generated.read_bytes().endswith(b"\n"))
            self.assertNotIn(b"\r", generated.read_bytes())


if __name__ == "__main__":
    unittest.main()
