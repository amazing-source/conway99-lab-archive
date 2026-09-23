from __future__ import annotations

import json
import tempfile
import unittest
from fractions import Fraction
from pathlib import Path

import independent_check as check


class Wave29S0IndependentTests(unittest.TestCase):
    def test_01_frozen_prior_hashes(self) -> None:
        self.assertEqual(check.verify_hashes(check.FROZEN_HASHES), check.FROZEN_HASHES)

    def test_02_preinspection_discovery_hashes(self) -> None:
        self.assertEqual(
            check.verify_hashes(check.DISCOVERY_HASHES), check.DISCOVERY_HASHES
        )

    def test_03_norm_four_support_split(self) -> None:
        result = check.frame_split()
        self.assertEqual(result["mixed_nonzero_norm_lower_bound"], 8)
        self.assertEqual(result["row_support"], "exactly_one_block")

    def test_04_tight_frame_row_counts(self) -> None:
        self.assertEqual(
            check.frame_split()["row_counts"], {"K12": 63, "LAMBDA_F": 168}
        )

    def test_05_exact_matrix_operation_control(self) -> None:
        result = check.small_matrix_split_certificate()
        self.assertEqual(result["Q"][0][1], 0)
        self.assertEqual(result["B"][1][0], 0)

    def test_06_unique_det_q(self) -> None:
        self.assertEqual(check.det_q_candidates(), [5])

    def test_07_rank_12_even_unimodular_veto(self) -> None:
        result = check.determinant_allocation()
        self.assertFalse(result["rank_12_even_unimodular_allowed"])
        self.assertEqual(result["survivor"], {"detQ_K": 5, "detQ_L": 1})

    def test_08_determinant_factors(self) -> None:
        factors = check.determinant_allocation()["determinant_factor_check"]
        self.assertEqual(factors["detB_K"], 3645)
        self.assertEqual(factors["detB_L"], 1)
        self.assertEqual(factors["detB_total"], factors["detS_times_detQ"])

    def test_09_row_alphabet_is_complete(self) -> None:
        rows = check.row_alphabet_table()
        self.assertEqual(len(rows), 13)
        self.assertEqual([r["c"] for r in rows], list(range(13)))

    def test_10_row_cube_residue(self) -> None:
        for row in check.row_alphabet_table():
            self.assertEqual(row["cube_sum"], 60 - 6 * row["c"])
            self.assertEqual(row["cube_sum"] % 6, 0)

    def test_11_exact_amgm_trace_pair(self) -> None:
        self.assertEqual(
            check.trace_pair_certificate()["exact_candidates"],
            [{"traceB_K": 24, "traceB_L": 36}],
        )

    def test_12_amgm_thresholds(self) -> None:
        self.assertFalse(check.amgm_allows(3645, 12, 18))
        self.assertTrue(check.amgm_allows(3645, 12, 24))
        self.assertFalse(check.amgm_allows(1, 32, 30))
        self.assertTrue(check.amgm_allows(1, 32, 36))

    def test_13_aggregate_block_couplings(self) -> None:
        result = check.aggregate_block_coupling_check()
        self.assertEqual(result["status"], "NO_ADDITIONAL_AGGREGATE_CONTRADICTION")
        self.assertEqual(
            result["blocks"]["K12"]["minimum_c_per_row_from_cross_zeros"], 2
        )
        for block in result["blocks"].values():
            self.assertEqual(
                block["directed_internal_total"],
                block["expected_directed_internal_total"],
            )
            self.assertTrue(block["all_internal_directed_counts_even"])

    def test_14_c_k_statement_does_not_assume_psd(self) -> None:
        c_k = check.derive()["C_K"]
        self.assertFalse(c_k["positive_semidefinite_assumed"])
        self.assertEqual(c_k["trace"], 6)
        self.assertIn("mu>-1/2", c_k["spectral_domain"])

    def test_15_pseudodeterminant_integrality(self) -> None:
        result = check.pseudodeterminant_certificate()
        self.assertIn("p(0)", result["consequence"])
        self.assertTrue(all(x["abs_p0"] >= 1 for x in result["exact_examples"]))

    def test_16_exact_log3_bounds(self) -> None:
        lower, upper = check.log3_rational_bounds()
        self.assertGreater(lower, Fraction(2, 3))
        self.assertLess(upper, 2)

    def test_17_positive_interval_derivative_identity(self) -> None:
        result = check.log_inequality_certificate()["positive_interval"]
        self.assertEqual(
            result["direct_coefficients"], result["factored_coefficients"]
        )
        self.assertEqual(result["minimum"], "F(1)=0")

    def test_18_negative_interval_is_explicit(self) -> None:
        result = check.log_inequality_certificate()["negative_interval"]
        self.assertEqual(result["domain"], "-1/2<x<0")
        self.assertIn("strict", result["conclusion"])
        self.assertIn("g(0)=0", result["orientation"])

    def test_19_final_determinant_contradiction(self) -> None:
        result = check.derive()["final_contradiction"]
        self.assertEqual(result["detB_K_forced"], 3645)
        self.assertEqual(result["detB_K_upper_bound"], 729)
        self.assertTrue(result["strict"])

    def test_20_every_premise_deletion_blocks(self) -> None:
        controls = check.hostile_controls()["premise_deletions"]
        self.assertEqual(set(controls), set(check.PREMISES))
        self.assertTrue(
            all(x["status"] == "BLOCKED_AS_REQUIRED" for x in controls.values())
        )

    def test_21_lower_minimum_breaks_support_split(self) -> None:
        control = check.hostile_controls()["lowered_block_minimum"]
        self.assertEqual(control["mixed_norm"], control["row_norm"])
        self.assertFalse(control["support_split_forced"])

    def test_22_missing_veto_removes_strict_contradiction(self) -> None:
        control = check.hostile_controls()["without_rank12_veto"]
        self.assertEqual(control["detB_K"], control["log_cap"])
        self.assertFalse(control["strict_contradiction"])

    def test_23_missing_trace_residue_removes_contradiction(self) -> None:
        control = check.hostile_controls()["without_trace_multiple_of_six"]
        self.assertEqual(control["trace_pair"], {"traceB_K": 28, "traceB_L": 32})
        self.assertFalse(control["strict_contradiction"])

    def test_24_nonintegral_c_breaks_pseudodeterminant_floor(self) -> None:
        control = check.hostile_controls()["without_C_integrality"]
        self.assertFalse(control["pseudodeterminant_ge_1"])
        self.assertTrue(control["exceeds_integral_cap_729"])

    def test_25_wrong_determinant_allocation_is_caught(self) -> None:
        control = check.hostile_controls()["determinant_allocation_swap"]
        self.assertEqual(control["incorrect_detB_K"], 729)
        self.assertIn("veto", control["result"])

    def test_26_scope_wall(self) -> None:
        result = check.build_results()
        verdict = result["verdict"]
        self.assertEqual(verdict["claim_label"], "VERIFIED")
        self.assertEqual(verdict["S0_full_projector_Schur_endpoint_origin"], "REFUTED")
        self.assertEqual(verdict["all_other_h_729_lattices"], "UNKNOWN")
        self.assertEqual(verdict["n3_equals_708"], "UNKNOWN")
        self.assertEqual(verdict["Conway_99"], "UNKNOWN")
        self.assertEqual(verdict["novelty"], "UNKNOWN")

    def test_27_deterministic_json_regeneration(self) -> None:
        expected_path = Path(__file__).with_name("independent-results.json")
        expected = expected_path.read_bytes()
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp) / "result.json"
            text = json.dumps(check.build_results(), indent=2, sort_keys=True) + "\n"
            output.write_text(text, encoding="utf-8", newline="\n")
            self.assertEqual(output.read_bytes(), expected)


if __name__ == "__main__":
    unittest.main()
