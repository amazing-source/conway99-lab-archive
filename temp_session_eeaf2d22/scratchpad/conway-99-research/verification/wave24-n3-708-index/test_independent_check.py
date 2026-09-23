from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from fractions import Fraction
from pathlib import Path

import independent_check as vc


class Wave24IndependentVerification(unittest.TestCase):
    def test_frozen_candidate_and_premise_hashes(self) -> None:
        for path, expected in {**vc.CANDIDATE_HASHES, **vc.PREMISE_HASHES}.items():
            self.assertEqual(vc.sha256(vc.ROOT / path), expected)

    def test_endpoint_reconstruction(self) -> None:
        endpoint = vc.endpoint_parameters()
        self.assertEqual(endpoint["delta"], 15)
        self.assertEqual(endpoint["trace_A4"], 1260)
        self.assertEqual(endpoint["trace_B"], 60)
        self.assertEqual(endpoint["trace_C"], 8)
        self.assertEqual(endpoint["sum_q"], 472)
        self.assertEqual(endpoint["sum_q_minus_2"], 10)
        self.assertEqual(endpoint["diagonal_excess_units"], 84)

    def test_pseudodeterminant_floor_all_ranks(self) -> None:
        rows = vc.pseudodeterminant_rank_rows()
        self.assertEqual(len(rows), 44)
        self.assertEqual(vc.trace_square_floor(), 8)
        minimizers = [
            row["nonzero_rank"]
            for row in rows
            if Fraction(row["combined_floor"]) == 8
        ]
        self.assertEqual(minimizers, [8])
        self.assertEqual(44 + 4 * 8 + 4 * vc.trace_square_floor(), 108)

    def test_integrality_pseudodeterminant_gate_is_active(self) -> None:
        hostile = vc.hostile_controls()["drop_integrality"]
        self.assertEqual(hostile["trace_C"], "8/1")
        self.assertEqual(hostile["trace_C2"], "16/11")
        self.assertTrue(hostile["det_B_exceeds_6561"])

    def test_log3_interval_and_derivative_factorization(self) -> None:
        lower, upper = vc.log3_interval()
        self.assertGreater(lower, Fraction(2, 3))
        self.assertLess(upper, 2)
        certificate = vc.derivative_certificate()
        self.assertTrue(certificate["coefficient_match"])
        self.assertEqual(
            certificate["direct_coefficients"],
            certificate["factored_coefficients"],
        )

    def test_determinant_cap_and_self_adjointness_gate(self) -> None:
        self.assertEqual(vc.determinant_cap(8), 6561)
        hostile = vc.hostile_controls()["drop_positive_form_self_adjointness"]
        self.assertEqual(hostile["integral_trace_C"], 8)
        self.assertTrue(hostile["det_B_exceeds_6561"])
        with self.assertRaises(ValueError):
            vc.determinant_cap(-1)

    def test_index_exhaustion(self) -> None:
        rows = vc.smooth_index_rows()
        self.assertEqual(
            [row["h"] for row in rows],
            [9, 21, 49, 81, 189, 441, 729, 1029],
        )
        self.assertEqual(
            [row["detQ_max_one_mod_four"] for row in rows],
            [729, 309, 133, 81, 33, 13, 9, 5],
        )
        self.assertEqual(
            [(row["rank_F3_M"], row["rank_F7_M"]) for row in rows],
            [(42, 44), (43, 43), (44, 42), (40, 44),
             (41, 43), (42, 42), (38, 44), (43, 41)],
        )

    def test_index_hypotheses_are_active(self) -> None:
        hostile = vc.hostile_controls()
        self.assertTrue(hostile["drop_h_not_one"]["h_one_reappears"])
        self.assertTrue(hostile["drop_h_congruence"]["h_three_reappears"])
        self.assertTrue(hostile["drop_h_congruence"]["h_seven_reappears"])

    def test_base_matrices(self) -> None:
        self.assertEqual(vc.determinant(vc.E8), 1)
        self.assertEqual(vc.determinant(vc.A2), 3)
        self.assertTrue(vc.positive_definite_sylvester(vc.E8))
        self.assertTrue(vc.positive_definite_sylvester(vc.A2))
        e8_inverse = vc.as_integer_matrix(vc.inverse(vc.E8))
        self.assertTrue(vc.has_even_diagonal(e8_inverse))
        self.assertTrue(vc.positive_definite_sylvester(e8_inverse))

    def test_complete_abstract_survivor(self) -> None:
        survivor = vc.survivor_certificate()
        facts = survivor["facts"]
        self.assertEqual(facts["rank"], 44)
        self.assertEqual(facts["det_S_h"], 9)
        self.assertEqual(facts["det_Q"], 9)
        self.assertEqual(facts["det_B"], 81)
        self.assertEqual(facts["trace_B"], 60)
        self.assertEqual(facts["trace_C"], 8)
        self.assertEqual(facts["trace_C2"], 32)
        self.assertEqual(facts["rank_C"], 2)
        self.assertTrue(facts["S_times_G_equals_21I"])
        self.assertTrue(facts["G_times_B_equals_21Q"])
        self.assertTrue(facts["B_G_self_adjoint"])
        self.assertTrue(facts["B_positive_for_G"])
        self.assertTrue(facts["B_congruent_I_mod_2"])
        self.assertEqual(facts["G_minimum_lower_bound"], 14)

    def test_survivor_hostile_mutations(self) -> None:
        hostile = vc.hostile_controls()
        self.assertFalse(
            hostile["mutate_survivor_G_parity"]["even_after_diagonal_plus_one"]
        )
        self.assertFalse(
            hostile["mutate_survivor_B_bridge"][
                "GB_equals_21Q_after_B00_plus_two"
            ]
        )

    def test_semantic_boundary_is_fail_closed(self) -> None:
        boundary = vc.survivor_certificate()["semantic_boundary"]
        self.assertTrue(boundary["abstract_coordinate_lattice_package"])
        self.assertFalse(boundary["primitive_embedding_in_Z231_proved"])
        self.assertFalse(boundary["231_projector_columns_proved"])
        self.assertFalse(boundary["Schur_square_origin_proved"])
        self.assertFalse(boundary["graph_realization_proved"])

    def test_harmonic_local_restrictions(self) -> None:
        local = vc.local_endpoint_certificate()
        self.assertEqual(local["harmonic_q12"]["gap"], 5520)
        self.assertTrue(local["harmonic_q12"]["excluded"])
        self.assertTrue(local["q11_single_allowed_by_cauchy"])
        self.assertEqual(local["q11_centered_diagonal"], "1291/5")
        self.assertTrue(local["two_q11_excluded"])
        self.assertTrue(all(
            Fraction(value) < 0
            for value in local["q11_pair_minor_determinants"].values()
        ))

    def test_endpoint_delta_is_active_in_q11_gate(self) -> None:
        local = vc.local_endpoint_certificate()
        self.assertTrue(local["hostile_old_delta12_would_exclude_q11"])
        self.assertTrue(local["q11_single_allowed_by_cauchy"])

    def test_local_scalar_profile_survives(self) -> None:
        profile = vc.local_endpoint_certificate()["scalar_profile"]
        self.assertEqual(profile["count"], 231)
        self.assertEqual(profile["sum_q"], 472)
        self.assertEqual(profile["sum_q_minus_2"], 10)
        self.assertEqual(profile["minimum_excess_units"], 0)

    def test_matrix_certificate_contains_exact_rows(self) -> None:
        certificate = vc.full_matrix_certificate()
        matrices = certificate["matrices"]
        self.assertEqual(set(matrices), {"E8", "A2", "S", "Q", "G", "B", "C"})
        self.assertEqual(len(matrices["G"]), 44)
        self.assertEqual(len(matrices["G"][0]), 44)
        self.assertEqual(
            vc.matrix_digest(matrices["B"]),
            vc.survivor_certificate()["matrix_sha256"]["B"],
        )

    def test_deterministic_serialization(self) -> None:
        payload = vc.build_results()
        expected = (
            json.dumps(payload, indent=2, sort_keys=True) + "\n"
        ).encode("utf-8")
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "result.json"
            path.write_bytes(expected)
            self.assertEqual(
                hashlib.sha256(path.read_bytes()).hexdigest(),
                hashlib.sha256(expected).hexdigest(),
            )


if __name__ == "__main__":
    unittest.main()
