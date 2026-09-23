from __future__ import annotations

import json
import tempfile
import unittest
from fractions import Fraction
from itertools import product
from pathlib import Path

import independent_check as check


class IndependentWave27VerifierTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.payload = check.build_results()

    def test_01_frozen_core_and_public_inputs(self) -> None:
        self.assertEqual(
            self.payload["frozen_submitted"],
            check.verify_hashes(check.ROOT, check.SUBMITTED),
        )
        self.assertEqual(
            self.payload["frozen_public_inputs"],
            check.verify_hashes(check.ROOT, check.PUBLIC_INPUTS),
        )

    def test_02_frozen_later_addendum(self) -> None:
        self.assertEqual(
            self.payload["frozen_addendum_submitted"],
            check.verify_hashes(check.ROOT, check.ADDENDUM_SUBMITTED),
        )

    def test_03_cartan_forms_and_independent_coordinate_controls(self) -> None:
        self.assertEqual(check.bareiss_det(check.CANONICAL_A6), 7)
        self.assertEqual(check.bareiss_det(check.CANONICAL_E6), 3)
        self.assertEqual(check.bareiss_det(check.CANONICAL_E8), 1)
        self.assertTrue(check.is_positive_definite(check.CANONICAL_A6))
        self.assertTrue(check.is_positive_definite(check.CANONICAL_E6))
        self.assertNotEqual(check.VERIFIER_A6, check.CANONICAL_A6)
        self.assertNotEqual(check.VERIFIER_E6, check.CANONICAL_E6)
        self.assertEqual(check.bareiss_det(check.VERIFIER_A6), 7)
        self.assertEqual(check.bareiss_det(check.VERIFIER_E6), 3)

    def test_04_projector_frame_block_moment_and_zero_sum(self) -> None:
        frame = self.payload["algebra"]["projector_frame_control"]
        self.assertEqual(frame["row_count"], 21)
        self.assertEqual(frame["second_moment"], [[14, 7], [7, 14]])
        self.assertEqual(frame["second_moment"], frame["expected_second_moment"])
        self.assertEqual(frame["row_sum"], [0, 0])

    def test_05_cross_Q_compression_identity(self) -> None:
        control = self.payload["algebra"]["arbitrary_cross_Q_control"]
        self.assertNotEqual(control["cross_Q_column"], [0, 0])
        self.assertEqual(
            control["local_trace"], control["first_leg_tensor_norm"]
        )
        self.assertLessEqual(
            control["pure_RRR_tensor_norm"],
            control["first_leg_tensor_norm"],
        )
        self.assertEqual(
            control["global_trace"],
            control["local_trace"] + control["complement_trace"],
        )
        self.assertGreater(control["compression_slack"], 0)

    def test_06_repeated_index_parity_is_necessary_including_aaa(self) -> None:
        for vector in product((0, 1), repeat=6):
            for a in range(6):
                for b in range(6):
                    self.assertEqual(
                        vector[a] ** 2 * vector[b] % 2,
                        vector[a] * vector[b] % 2,
                    )
        triples = check.triples_lex(6)
        residues, moduli, moment = check.parity_coset(
            check.CANONICAL_E6, triples
        )
        for i, (a, b, c) in enumerate(triples):
            if a == b:
                self.assertEqual(moduli[i], 2)
                self.assertEqual(residues[i], moment[a][c] % 2)
            elif b == c:
                self.assertEqual(moduli[i], 2)
                self.assertEqual(residues[i], moment[b][a] % 2)
            else:
                self.assertEqual(moduli[i], 1)
        aaa = [i for i, (a, b, c) in enumerate(triples) if a == b == c]
        self.assertEqual(len(aaa), 6)
        self.assertTrue(all(moduli[i] == 2 for i in aaa))

    def test_07_exact_symmetric_cubic_gram_and_declared_hashes(self) -> None:
        hashes = self.payload["algebra"]["canonical_gram_hashes"]
        self.assertEqual(hashes, {
            "A6": check.DECLARED_CANONICAL_GRAM_HASHES["A6"],
            "E6": check.DECLARED_CANONICAL_GRAM_HASHES["E6"],
        })
        for form in (check.CANONICAL_E6, check.CANONICAL_A6):
            triples = check.triples_lex(6)
            gram = check.symmetric_cubic_gram(form, triples)
            coefficients = [((17 * i + 11) % 9) - 4
                            for i in range(len(triples))]
            direct = check.direct_tensor_norm(form, triples, coefficients)
            matrix = int(check.quadratic(gram, coefficients))
            self.assertEqual(direct, matrix)

    def test_08_permuted_coordinate_tensor_norm_invariance(self) -> None:
        canonical_triples = check.triples_lex(6)
        old_coefficients = {
            triple: ((19 * i + 3) % 11) - 5
            for i, triple in enumerate(canonical_triples)
        }
        for old_form, new_form, order in (
            (check.CANONICAL_A6, check.VERIFIER_A6, check.A6_COORDINATE_ORDER),
            (check.CANONICAL_E6, check.VERIFIER_E6, check.E6_COORDINATE_ORDER),
        ):
            new_triples = check.triples_lex(6)
            new_coefficients = [
                old_coefficients[tuple(sorted(order[i] for i in triple))]
                for triple in new_triples
            ]
            old_vector = [old_coefficients[t] for t in canonical_triples]
            self.assertEqual(
                check.direct_tensor_norm(old_form, canonical_triples, old_vector),
                check.direct_tensor_norm(new_form, new_triples, new_coefficients),
            )

    def test_09_exact_integer_interval_matches_brute_force(self) -> None:
        centers = [
            Fraction(-7, 3), Fraction(-1, 2), Fraction(0),
            Fraction(5, 4), Fraction(13, 5),
        ]
        radii = [
            Fraction(0), Fraction(1, 7), Fraction(1),
            Fraction(17, 6), Fraction(25, 4),
        ]
        for center in centers:
            for radius2 in radii:
                low, high = check.integer_interval(center, radius2)
                exact = [
                    z for z in range(-20, 21)
                    if (Fraction(z) + center) ** 2 <= radius2
                ]
                interval = list(range(low, high + 1))
                self.assertEqual(interval, exact)

    def test_10_affine_cvp_small_boundary_positive_control(self) -> None:
        rank_one = [[2]]
        below = check.affine_cvp_search(rank_one, 7, scale=2)
        boundary = check.affine_cvp_search(
            rank_one, 8, scale=2, stop_after_first=True
        )
        self.assertFalse(below["found"])
        self.assertEqual(below["complete_leaves"], 0)
        self.assertTrue(boundary["found"])
        self.assertEqual(boundary["witness_norm"], 8)
        self.assertEqual(boundary["complete_leaves"], 1)

    def test_11_E6_closed_parity_ball_is_empty(self) -> None:
        result = self.payload["searches"]["E6_cap_18"]
        self.assertFalse(result["found"])
        self.assertEqual(result["cap"], 18)
        self.assertEqual(result["accepted_partial_nodes"], 10011)
        self.assertEqual(result["complete_leaves"], 0)
        self.assertEqual(result["odd_repeated_coordinates"], 10)
        self.assertEqual(result["free_coordinates"], 20)

    def test_12_A6_closed_parity_ball_is_empty(self) -> None:
        result = self.payload["searches"]["A6_cap_60"]
        self.assertFalse(result["found"])
        self.assertEqual(result["cap"], 60)
        self.assertEqual(result["accepted_partial_nodes"], 105185)
        self.assertEqual(result["complete_leaves"], 0)
        self.assertEqual(result["odd_repeated_coordinates"], 12)
        self.assertEqual(result["free_coordinates"], 20)

    def test_13_even_scale_zero_tensor_controls(self) -> None:
        hostile = self.payload["hostile_controls"]
        for key in ("even_scale_E6_zero_tensor", "even_scale_A6_zero_tensor"):
            self.assertTrue(hostile[key]["found"])
            self.assertEqual(hostile[key]["witness_norm"], 0)
            self.assertEqual(hostile[key]["complete_leaves"], 1)

    def test_14_zero_sum_energy_divisibility_and_hostile_drop(self) -> None:
        row = self.payload["energy_divisibility"]
        self.assertTrue(row["all_k_cubed_congruent_k_mod_6"])
        self.assertEqual(row["zero_sum_frame_energy"], 18)
        self.assertEqual(row["zero_sum_frame_energy_mod_6"], 0)
        self.assertEqual(row["drop_zero_sum_counterexample_energy"], 8)
        self.assertEqual(row["drop_zero_sum_counterexample_mod_6"], 2)

    def test_15_floors_and_rank_complement_cap(self) -> None:
        floors = self.payload["tensor_floors"]
        self.assertEqual(floors["E6"]["floor"], 24)
        self.assertEqual(floors["E6"]["rank_complement_cap"], 22)
        self.assertGreater(24, 22)
        self.assertEqual(floors["A6"]["floor"], 66)
        self.assertGreater(66, 60)
        for rank in range(1, 44):
            self.assertEqual(60 - (44 - rank), rank + 16)
        # If the complement determinant were merely 1/4 rather than a
        # positive integer, a rank-one trace of 1/4 would defeat the floor 1.
        self.assertLess(Fraction(1, 4), 1)

    def test_16_trace_14_E6_hostile_algebraic_block(self) -> None:
        row = self.payload["hostile_controls"]["trace_14_E6_algebraic_block"]
        self.assertTrue(row["P_idempotent"])
        self.assertTrue(row["Q_even_integral_PD"])
        self.assertEqual(row["trace_RQ"], 14)
        self.assertEqual(row["det_Q"], 3)
        self.assertEqual(row["det_RQ"], 9)

    def test_17_complete_ADE_integrality_evenness_screen(self) -> None:
        screen = self.payload["ADE_component_screen"]
        self.assertEqual(screen["candidate_count"], 88)
        self.assertEqual(screen["accepted_count"], 5)
        self.assertEqual(screen["rejected_count"], 83)
        self.assertEqual(
            [row["type"] for row in screen["accepted"]],
            ["A2", "A6", "A20", "E6", "E8"],
        )
        self.assertTrue(all(
            row["21_inverse_integral"]
            and row["21_inverse_even_diagonal"]
            for row in screen["accepted"]
        ))

    def test_18_complete_rank_determinant_census(self) -> None:
        census = self.payload["submitted_scope_full_ADE_census"]
        self.assertEqual(census["total_cases"], 17)
        self.assertEqual(
            census["counts"],
            {"9": 2, "21": 2, "49": 1, "81": 2,
             "189": 3, "441": 2, "729": 4, "1029": 1},
        )
        for h_text, rows in census["decompositions"].items():
            h = int(h_text)
            for components in rows:
                rank = 0
                determinant = 1
                by_name = {name: (r, d) for name, r, d in check.COMPONENTS}
                for name, count in components.items():
                    r, d = by_name[name]
                    rank += count * r
                    determinant *= d ** count
                self.assertEqual(rank, 44)
                self.assertEqual(determinant, h)

    def test_19_submitted_screen_survivor_is_exactly_one(self) -> None:
        survivors = self.payload["submitted_scope_full_ADE_census"]["survivors"]
        self.assertEqual(survivors, [{
            "h": 21,
            "components": {"A20": 1, "E8": 3},
            "status": "SURVIVES_SUBMITTED_SCREEN",
        }])

    def test_20_A_n_rank_one_factorization_and_trace_identity(self) -> None:
        for n in range(1, 45):
            vectors: list[list[int]] = []
            first = [0] * n
            first[0] = 1
            vectors.append(first)
            for i in range(n - 1):
                difference = [0] * n
                difference[i] = 1
                difference[i + 1] = -1
                vectors.append(difference)
            last = [0] * n
            last[-1] = 1
            vectors.append(last)
            reconstructed = [
                [sum(v[i] * v[j] for v in vectors) for j in range(n)]
                for i in range(n)
            ]
            self.assertEqual(reconstructed, check.cartan_a(n))
            q = [
                [2 * int(i == j) + 2 for j in range(n)]
                for i in range(n)
            ]
            identity = check.a_n_trace_identity(n, q)
            self.assertEqual(identity["term_count"], n + 1)
            self.assertEqual(identity["trace_AQ"], sum(identity["terms"]))

    def test_21_A20_addendum_and_evenness_hostile_control(self) -> None:
        addendum = self.payload["orchestrator_addendum"]
        self.assertEqual(addendum["status"], "VERIFIED_ORCHESTRATOR_ADDENDUM")
        self.assertEqual(addendum["A20_local_floor"], 42)
        self.assertEqual(addendum["rank_24_complement_floor"], 24)
        self.assertEqual(addendum["global_floor"], 66)
        self.assertGreater(addendum["global_floor"], addendum["global_trace"])
        # Q=I is integral PD but not even; its trace is only 2n<2(n+1).
        odd_q = check.identity(20)
        odd_control = check.a_n_trace_identity(20, odd_q)
        self.assertEqual(odd_control["trace_AQ"], 40)
        self.assertLess(odd_control["trace_AQ"], 42)

    def test_22_status_and_scope_walls(self) -> None:
        scope = self.payload["scope"]
        self.assertEqual(
            scope["submitted_A20_E8_cubed_survivor"],
            "CORRECTLY_SURVIVES_THE_SUBMITTED_COMPONENT_SCREEN",
        )
        self.assertEqual(
            scope["stronger_addendum_result"],
            "EXCLUDED_BY_A20_TRACE_IDENTITY_PLUS_COMPLEMENT",
        )
        self.assertEqual(scope["general_even_rank_44_lattices"], "UNKNOWN")
        self.assertEqual(scope["n3_708"], "UNKNOWN")
        self.assertEqual(scope["Conway_99"], "UNKNOWN")
        self.assertEqual(scope["novelty"], "UNKNOWN")
        self.assertEqual(
            self.payload["hostile_controls"]["nonorthogonal_root_subsystem"],
            "OUT_OF_SCOPE_NO_BLOCK_MOMENT",
        )

    def test_23_deterministic_LF_only_json(self) -> None:
        text = check.canonical_json(self.payload)
        self.assertNotIn("\r\n", text)
        self.assertEqual(json.loads(text), self.payload)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "result.json"
            path.write_text(text, encoding="utf-8", newline="\n")
            self.assertEqual(path.read_bytes(), text.encode("utf-8"))


if __name__ == "__main__":
    unittest.main()
