#!/usr/bin/env python3
"""Tests for the independent Wave 27 E6 trace-floor audit."""

from __future__ import annotations

import json
import tempfile
import unittest
from fractions import Fraction
from pathlib import Path

import independent_check as check


class Wave27E6TraceVerifier(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = check.build_result()
        check.validate(cls.result)

    def test_01_discovery_freeze(self) -> None:
        self.assertTrue(self.result["frozen_discovery"]["all_match"])
        self.assertEqual(
            len(self.result["frozen_discovery"]["files"]),
            7,
        )

    def test_02_e6_inverse_and_determinant(self) -> None:
        local = self.result["local_equality"]
        self.assertEqual(local["det_E6"], 3)
        self.assertTrue(local["inverse_check"])

    def test_03_equality_vector_norm(self) -> None:
        self.assertEqual(self.result["local_equality"]["v_H_v"], "4/3")

    def test_04_projector_is_independently_reconstructed(self) -> None:
        local = self.result["local_equality"]
        self.assertEqual(local["P_rank"], 1)
        self.assertTrue(local["P_idempotent"])
        self.assertTrue(local["P_H_self_adjoint"])

    def test_05_displayed_matrices_are_exact(self) -> None:
        local = self.result["local_equality"]
        self.assertTrue(local["B_equals_display"])
        self.assertTrue(local["Q_equals_display"])

    def test_06_q6_is_an_even_positive_form(self) -> None:
        self.assertTrue(
            self.result["local_equality"]["Q_symmetric_even_integral_PD"]
        )

    def test_07_b6_parity_and_self_adjointness(self) -> None:
        local = self.result["local_equality"]
        self.assertTrue(local["B_identity_mod_two"])
        self.assertTrue(local["B_Q_self_adjoint"])

    def test_08_b6_spectrum_certificate(self) -> None:
        local = self.result["local_equality"]
        self.assertTrue(local["B_spectral_polynomial"])
        self.assertEqual(local["det_B"], 9)
        self.assertEqual(local["trace_B"], 14)

    def test_09_local_determinants_and_c_moments(self) -> None:
        local = self.result["local_equality"]
        self.assertEqual(local["det_Q"], 3)
        self.assertEqual(local["trace_C"], 4)
        self.assertEqual(local["trace_C_squared"], 16)

    def test_10_rank_six_determinant_and_trace_congruences(self) -> None:
        proof = self.result["proof_branches"]
        self.assertEqual(
            proof["rank_six_even_odd_det_residue_Q_mod_4"],
            3,
        )
        self.assertEqual(proof["det_B_mod_4"], 1)
        self.assertEqual(proof["trace_B_mod_4"], 2)

    def test_11_low_trace_am_gm_branch(self) -> None:
        proof = self.result["proof_branches"]
        self.assertEqual(proof["det_B_floor"], 9)
        self.assertTrue(proof["T_at_most_8_AM_GM_contradiction"])

    def test_12_pseudodeterminant_floor(self) -> None:
        branch = self.result["proof_branches"]["trace_C_square_floor_two"]
        self.assertTrue(branch["all_strictly_below_one"])

    def test_13_trace_square_two_forces_idempotent(self) -> None:
        branch = self.result["proof_branches"]["trace_C_square_equals_two"]
        self.assertTrue(branch["all_strictly_below_one"])
        self.assertEqual(branch["therefore_rank_two_spectrum"], ["1", "1"])
        self.assertTrue(branch["therefore_integral_idempotent"])

    def test_14_rank_four_kernel_obstruction(self) -> None:
        branch = self.result["proof_branches"]["rank_four_kernel_obstruction"]
        self.assertTrue(all(branch.values()))

    def test_15_required_parity_bridge_is_recorded(self) -> None:
        branch = self.result["proof_branches"][
            "required_trace_square_parity_bridge"
        ]
        self.assertTrue(branch["bridge_valid"])
        self.assertTrue(branch["after_excluding_two_floor_is_four"])
        self.assertTrue(branch["omitted_from_discovery_prose"])

    def test_16_kkt_product_candidates(self) -> None:
        branch = self.result["proof_branches"]["KKT_determinant_bound_at_T_10"]
        self.assertTrue(branch["k2_below_5"])
        self.assertTrue(branch["k3_below_5"])
        self.assertFalse(branch["k4_or_k5_positive_candidate"])
        self.assertEqual(branch["det_B_upper"], 5)
        self.assertTrue(branch["contradicts_det_B_floor"])

    def test_17_trace_floor_and_equality(self) -> None:
        conclusion = self.result["proof_branches"]["conclusion"]
        self.assertEqual(conclusion["trace_values_before_14"], [2, 6, 10])
        self.assertTrue(conclusion["all_excluded"])
        self.assertEqual(conclusion["minimum"], 14)
        self.assertEqual(conclusion["equality_witness_trace"], 14)

    def test_18_full_block_arithmetic(self) -> None:
        full = self.result["rank_44_crosscheck"]
        self.assertEqual(full["rank"], 44)
        self.assertEqual(
            full["determinants_from_blocks"],
            {"S": 9, "Q": 9, "B": 81},
        )
        self.assertEqual(full["rank_mod_3_S"], 42)
        self.assertTrue(full["S_H_identity"])
        self.assertTrue(full["S_G_equals_21I"])
        self.assertTrue(full["S_Q_equals_B"])
        self.assertTrue(full["G_B_equals_21Q"])

    def test_19_full_moments_and_digests(self) -> None:
        full = self.result["rank_44_crosscheck"]
        self.assertEqual(full["trace_B"], 60)
        self.assertEqual(full["trace_C"], 8)
        self.assertEqual(full["trace_C_squared"], 32)
        self.assertEqual(full["rank_C"], 2)
        self.assertTrue(full["digests_match_discovery"])

    def test_20_scope_wall(self) -> None:
        wall = self.result["scope_wall"]
        self.assertFalse(wall["all_h9_forms_classified"])
        self.assertFalse(wall["projector_or_Schur_origin_constructed"])
        self.assertFalse(wall["n3_708_excluded"])
        self.assertEqual(wall["Conway_99_status"], "UNKNOWN")
        self.assertEqual(wall["novelty"], "UNKNOWN")

    def test_21_deterministic_lf_json(self) -> None:
        expected = json.dumps(
            self.result,
            indent=2,
            sort_keys=True,
        ) + "\n"
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "result.json"
            output.write_text(expected, encoding="utf-8", newline="\n")
            actual = output.read_bytes()
        self.assertEqual(actual, expected.encode("utf-8"))
        self.assertTrue(actual.endswith(b"\n"))
        self.assertNotIn(b"\r\n", actual)


if __name__ == "__main__":
    unittest.main()
