#!/usr/bin/env python3
"""Hostile exact tests for the Wave 29 S0 frame exclusion."""

from __future__ import annotations

import json
import tempfile
import unittest
from fractions import Fraction
from pathlib import Path

import exact_check as check


class Wave29S0FrameExclusionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = check.build_result()
        cls.derivation = cls.result["derivation"]

    def test_all_frozen_input_hashes(self) -> None:
        self.assertEqual(
            self.result["frozen_inputs"],
            check.FROZEN_INPUTS,
        )

    def test_frozen_s0_block_facts(self) -> None:
        facts = self.result["single_lattice_scope"]
        self.assertEqual(facts["K12"]["rank"], 12)
        self.assertEqual(facts["K12"]["determinant"], 729)
        self.assertEqual(facts["K12"]["minimum"], 4)
        self.assertEqual(facts["LAMBDA_F"]["rank"], 32)
        self.assertEqual(facts["LAMBDA_F"]["determinant"], 1)
        self.assertEqual(facts["LAMBDA_F"]["minimum"], 4)
        self.assertEqual(facts["S0"]["rank"], 44)
        self.assertEqual(facts["S0"]["determinant"], 729)

    def test_norm_four_and_tight_frame_block_split(self) -> None:
        split = self.derivation["frame_split"]
        self.assertEqual(split["K12_rows"], 63)
        self.assertEqual(split["LAMBDA_F_rows"], 168)
        self.assertEqual(split["total_rows"], 231)
        self.assertTrue(split["no_automorphism_or_search_assumption"])

    def test_M_W_Q_B_block_split(self) -> None:
        blocks = self.derivation["matrix_split"]["after_row_permutation"]
        self.assertEqual(set(blocks), {"X", "M", "W", "Q", "B"})
        self.assertIn("diag(M_K,M_L)", blocks["M"])
        self.assertIn("diag", blocks["W"])
        self.assertIn("diag", blocks["Q"])
        self.assertIn("diag", blocks["B"])

    def test_detQ_is_exactly_five(self) -> None:
        certificate = self.derivation["detQ"]
        self.assertEqual(certificate["detQ_candidates"], [5])
        self.assertEqual(certificate["detQ"], 5)
        self.assertLessEqual(729 * 5, 6525)

    def test_rank_twelve_even_unimodular_veto_allocates_determinants(self) -> None:
        allocation = self.derivation["determinant_allocation"]
        self.assertEqual(
            allocation["pre_veto_allocations"],
            [{"detQ_K": 1, "detQ_L": 5}, {"detQ_K": 5, "detQ_L": 1}],
        )
        self.assertEqual(
            allocation["survivor"],
            {"detQ_K": 5, "detQ_L": 1},
        )
        self.assertEqual(allocation["detB_K"], 3645)
        self.assertEqual(allocation["detB_L"], 1)

    def test_per_row_alphabet_equations_complete(self) -> None:
        table = self.derivation["row_alphabet"]["admissible_table"]
        self.assertEqual(len(table), 13)
        for row in table:
            c_value = row["c_minus_two"]
            self.assertEqual(row["a_plus_one"], 32 - c_value)
            self.assertEqual(row["b_minus_one"], 36 - 3 * c_value)
            self.assertEqual(row["z_zero"], 162 + 3 * c_value)
            self.assertEqual(row["row_cube_sum"], 60 - 6 * c_value)
            self.assertEqual(
                row["a_plus_one"]
                + row["b_minus_one"]
                + row["c_minus_two"]
                + row["z_zero"],
                230,
            )

    def test_block_traces_are_forced_to_24_and_36(self) -> None:
        traces = self.derivation["block_traces"]
        self.assertTrue(traces["positive_multiples_of_six"])
        self.assertEqual(
            traces["exact_candidates"],
            [{"traceB_K": 24, "traceB_L": 36}],
        )
        self.assertEqual(traces["sum_c_K"], 626)
        self.assertEqual(traces["sum_c_L"], 1674)
        self.assertEqual(traces["sum_c_total"], 2300)

    def test_AM_GM_comparisons_are_exact_integers(self) -> None:
        self.assertFalse(check.amgm_feasible(12, 3645, 18))
        self.assertTrue(check.amgm_feasible(12, 3645, 24))
        self.assertFalse(check.amgm_feasible(32, 1, 30))
        self.assertTrue(check.amgm_feasible(32, 1, 36))

    def test_CK_statement_does_not_inflate_positivity(self) -> None:
        c_block = self.derivation["logarithmic_contradiction"]["C_K"]
        self.assertTrue(c_block["integral"])
        self.assertTrue(c_block["G_K_self_adjoint"])
        self.assertTrue(c_block["real_diagonalizable"])
        self.assertFalse(c_block["positive_semidefinite"])
        self.assertEqual(c_block["trace"], 6)
        self.assertIn("strictly greater than -1/2", c_block["correct_positivity_statement"])

    def test_integral_characteristic_pseudodeterminant(self) -> None:
        pseudo = self.derivation["logarithmic_contradiction"][
            "characteristic_pseudodeterminant"
        ]
        self.assertIn("p monic in Z[t]", pseudo["factorization"])
        self.assertIn(">=1", pseudo["nonzero_eigenvalue_product"])

    def test_exact_log3_interval(self) -> None:
        lower, upper = check.log3_bounds(12)
        self.assertGreater(lower, Fraction(2, 3))
        self.assertLess(upper, 2)
        self.assertLess(lower, upper)

    def test_formal_positive_domain_derivative_factorization(self) -> None:
        certificate = check.derivative_factorization_certificate()
        self.assertEqual(
            certificate["direct_coefficients_ascending"],
            certificate["factored_coefficients_ascending"],
        )
        self.assertEqual(
            certificate["identity"],
            "x(1+2x)F'(x)=(x-1)(2Lx+L-2/3)",
        )

    def test_logarithmic_determinant_contradiction(self) -> None:
        certificate = self.derivation["logarithmic_contradiction"]
        self.assertEqual(certificate["detB_K_upper_bound"], 729)
        self.assertEqual(certificate["detB_K_forced"], 3645)
        self.assertGreater(
            certificate["detB_K_forced"],
            certificate["detB_K_upper_bound"],
        )

    def test_every_essential_premise_deletion_fails_closed(self) -> None:
        controls = self.result["hostile_controls"]
        for premise in check.ESSENTIAL_PREMISES:
            self.assertEqual(
                controls[premise]["status"],
                "BLOCKED_AS_REQUIRED",
            )
            self.assertIn(premise, controls[premise]["first_failed_stage"])

    def test_nonintegral_C_and_veto_deletion_controls(self) -> None:
        controls = self.result["hostile_controls"]
        fractional = controls["explicit_nonintegral_C_control"]
        self.assertEqual(fractional["traceC"], 6)
        self.assertEqual(fractional["detB"], 4096)
        self.assertTrue(fractional["exceeds_integral_log_cap_729"])
        no_veto = controls["without_even_unimodular_veto"]
        self.assertEqual(no_veto["detB_K"], no_veto["log_cap"])
        self.assertFalse(no_veto["strict_contradiction"])
        no_residue = controls["without_trace_multiple_of_six"]
        self.assertGreater(
            no_residue["generic_log_cap"],
            no_residue["forced_detB_K"],
        )
        self.assertFalse(no_residue["contradiction"])

    def test_scope_wall(self) -> None:
        verdict = self.result["verdict"]
        self.assertEqual(
            verdict["S0_full_projector_Schur_endpoint_origin"],
            "REFUTED_DERIVED",
        )
        for key in ("all_h_729_lattices", "n3_equals_708", "Conway_99", "novelty"):
            self.assertEqual(verdict[key], "UNKNOWN")
        self.assertTrue(verdict["independent_verification_required"])

    def test_deterministic_json(self) -> None:
        first = check.canonical_json(check.build_result())
        second = check.canonical_json(check.build_result())
        self.assertEqual(first, second)
        json.loads(first)
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "result.json"
            output.write_text(first, encoding="utf-8", newline="\n")
            self.assertEqual(output.read_bytes(), first.encode("utf-8"))


if __name__ == "__main__":
    unittest.main()
