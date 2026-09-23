from __future__ import annotations

import json
import tempfile
import unittest
from fractions import Fraction
from itertools import product
from pathlib import Path

import exact_check as check


class Wave27GeneralRootTensorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.payload = check.build_results()

    def test_public_base_and_frozen_inputs(self) -> None:
        self.assertEqual(
            self.payload["base_commit"],
            "2ac11809fafee7ab752965ae49a96e922859b5ee",
        )
        self.assertEqual(
            self.payload["frozen_inputs"],
            check.validate_frozen_inputs(),
        )

    def test_cartan_determinants_and_dual_integrality(self) -> None:
        self.assertEqual(check.determinant(check.A6), 7)
        self.assertEqual(check.determinant(check.E6), 3)
        self.assertEqual(check.determinant(check.E8), 1)
        for form in (check.A6, check.E6, check.E8):
            self.assertTrue(check.is_positive_definite(form))
            self.assertTrue(check.is_even(form))

    def test_complete_ADE_discriminant_screen(self) -> None:
        rows = self.payload["ADE_discriminant_screen"][
            "allowed_irreducible_components"
        ]
        self.assertEqual(
            [row["type"] for row in rows],
            ["A2", "A6", "A20", "E6", "E8"],
        )
        self.assertEqual(
            self.payload["ADE_discriminant_screen"][
                "rejected_component_count"
            ],
            83,
        )

    def test_symmetric_tensor_gram_matches_direct_ordered_expansion(self) -> None:
        triples, gram = check.symmetric_cubic_gram(check.E6)
        coefficients = [
            ((13 * index + 5) % 7) - 3 for index in range(len(triples))
        ]
        tensor = [[[0] * 6 for _ in range(6)] for _ in range(6)]
        for coefficient, triple in zip(coefficients, triples):
            for a, b, c in check.ordered_orbit(triple):
                tensor[a][b][c] = coefficient
        direct = 0
        for a, b, c, d, e, f in product(range(6), repeat=6):
            direct += (
                tensor[a][b][c]
                * check.E6[a][d]
                * check.E6[b][e]
                * check.E6[c][f]
                * tensor[d][e][f]
            )
        matrix_value = sum(
            coefficients[i] * gram[i][j] * coefficients[j]
            for i in range(len(triples))
            for j in range(len(triples))
        )
        self.assertEqual(direct, matrix_value)

    def test_exact_LDL_reconstruction_for_both_rank_six_forms(self) -> None:
        for form in (check.E6, check.A6):
            _, gram = check.symmetric_cubic_gram(form)
            lower, diagonal = check.ldl(gram)
            self.assertTrue(all(value > 0 for value in diagonal))
            self.assertEqual(
                check.reconstruct_ldl(lower, diagonal),
                [[Fraction(value) for value in row] for row in gram],
            )

    def test_frame_parity_identity_by_exhaustive_binary_vectors(self) -> None:
        # For every binary coordinate vector, z_a^2 z_b=z_a z_b.
        for vector in product((0, 1), repeat=6):
            for a in range(6):
                for b in range(6):
                    self.assertEqual(
                        (vector[a] ** 2 * vector[b]) % 2,
                        (vector[a] * vector[b]) % 2,
                    )

    def test_E6_exact_empty_ball_and_floor(self) -> None:
        row = self.payload["tensor_component_floors"]["E6"]
        self.assertTrue(row["closed_ball_empty"])
        self.assertEqual(row["parity_coset_closed_ball_cap"], 18)
        self.assertEqual(row["actual_energy_floor"], 24)
        self.assertEqual(row["global_complement_upper_bound"], 22)
        self.assertEqual(row["orthogonal_E6_summand"], "REFUTED")
        self.assertEqual(
            row["enumeration"]["accepted_partial_nodes"],
            10011,
        )
        self.assertEqual(row["enumeration"]["complete_leaves"], 0)

    def test_A6_exact_empty_ball_and_floor(self) -> None:
        row = self.payload["tensor_component_floors"]["A6"]
        self.assertTrue(row["closed_ball_empty"])
        self.assertEqual(row["parity_coset_closed_ball_cap"], 60)
        self.assertEqual(row["actual_energy_floor"], 66)
        self.assertEqual(row["orthogonal_A6_summand"], "REFUTED")
        self.assertEqual(
            row["enumeration"]["accepted_partial_nodes"],
            105185,
        )
        self.assertEqual(row["enumeration"]["complete_leaves"], 0)

    def test_exact_interval_enumerator_finds_relaxed_zero_tensor(self) -> None:
        # Even replacement scales make all forced repeated-coordinate
        # parities zero. The zero tensor must then be found in the zero ball.
        e6_relaxed = check.enumerate_affine_sphere(
            check.E6, bound=0, scale_value=18
        )
        a6_relaxed = check.enumerate_affine_sphere(
            check.A6, bound=0, scale_value=14
        )
        self.assertTrue(e6_relaxed["found_tensor_in_closed_ball"])
        self.assertEqual(e6_relaxed["witness_norm"], 0)
        self.assertTrue(a6_relaxed["found_tensor_in_closed_ball"])
        self.assertEqual(a6_relaxed["witness_norm"], 0)

    def test_cubic_energy_divisibility_mod_six(self) -> None:
        for value in range(-200, 201):
            self.assertEqual((value ** 3 - value) % 6, 0)
        row = self.payload["tensor_component_floors"][
            "zero_sum_energy_divisibility"
        ]
        self.assertIn("6*Z", row["conclusion"])

    def test_rank_one_E6_trace_14_counterexample(self) -> None:
        row = check.rank_one_projection_block()
        self.assertEqual(row["trace_B"], 14)
        self.assertEqual(row["det_B"], 9)
        self.assertEqual(row["det_Q"], 3)
        self.assertEqual(row["B_mod_2"], "identity")
        self.assertTrue(row["Q_integral_even_positive_definite"])
        self.assertEqual(
            self.payload["hostile_controls"][
                "naive_E6_algebraic_trace_floor"
            ]["status"],
            "REFUTED",
        )

    def test_general_complement_budget(self) -> None:
        # For rank r, positive integral determinant on the complement gives
        # trace at least 44-r. Thus the local endpoint budget is r+16.
        for rank in range(1, 44):
            complement = 44 - rank
            local_upper = 60 - complement
            self.assertEqual(local_upper, rank + 16)
        self.assertLess(6 + 16, 24)

    def test_A2_capacity_specialization(self) -> None:
        row = check.a2_frame_capacity()
        self.assertEqual(row["forced_root_incident_rows"], 21)
        self.assertEqual(row["capacity"], 18)
        self.assertEqual(
            row["status"], "REFUTED_AS_ORTHOGONAL_SUMMAND"
        )

    def test_rank_44_ADE_census_and_unique_conditional_survivor(self) -> None:
        screen = self.payload["full_rank_44_ADE_screen"]
        cases = screen["classified_cases"]
        self.assertEqual(len(cases), 17)
        self.assertEqual(
            screen["survivors_of_this_screen"],
            [
                {
                    "h": 21,
                    "components": {"A20": 1, "E8": 3},
                    "local_trace_floor": 48,
                    "status": "SURVIVES_THIS_CONDITIONAL_SCREEN",
                }
            ],
        )
        e6_cases = [
            row for row in cases
            if row["components"].get("E6", 0)
            and not row["components"].get("A2", 0)
            and not row["components"].get("A6", 0)
        ]
        self.assertTrue(e6_cases)
        self.assertTrue(
            all(
                row["status"]
                == "EXCLUDED_BY_E6_LOCAL_FLOOR_24_VS_GLOBAL_CAP_22"
                for row in e6_cases
            )
        )

    def test_nonorthogonal_and_norm_four_scope_guards(self) -> None:
        hostile = self.payload["hostile_controls"]
        self.assertEqual(
            hostile["nonorthogonal_root_subsystem"]["status"],
            "NO_CLAIM",
        )
        self.assertTrue(
            hostile["norm_four_vectors"][
                "tensor_parity_method_uses_norm_four_vectors_safely"
            ]
        )
        limitations = " ".join(self.payload["limitations"])
        self.assertIn("nonorthogonal root subsystem", limitations)
        self.assertIn("A20 orthogonal_sum E8^3", limitations)

    def test_no_endpoint_or_target_promotion(self) -> None:
        claim = self.payload["claim"]
        self.assertEqual(claim["label"], "DERIVED")
        self.assertEqual(claim["endpoint_status"], "UNKNOWN")
        self.assertEqual(claim["novelty_status"], "UNKNOWN")
        limitations = " ".join(self.payload["limitations"])
        self.assertIn("n3=708", limitations)
        self.assertIn("Conway-99", limitations)

    def test_deterministic_LF_only_json(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            first = Path(directory) / "first.json"
            second = Path(directory) / "second.json"
            check.write_results(first, self.payload)
            check.write_results(second, check.build_results())
            self.assertEqual(first.read_bytes(), second.read_bytes())
            self.assertNotIn(b"\r\n", first.read_bytes())
            parsed = json.loads(first.read_text(encoding="utf-8"))
            self.assertEqual(parsed, self.payload)


if __name__ == "__main__":
    unittest.main()
