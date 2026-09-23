from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from fractions import Fraction
from pathlib import Path

import exact_check as ec


class Wave25StrictnessChecks(unittest.TestCase):
    def test_frozen_inputs_match(self) -> None:
        self.assertEqual(len(ec.INPUTS), 7)
        for path, expected in ec.INPUTS.items():
            self.assertEqual(ec.sha256(ec.ROOT / path), expected)

    def test_endpoint_arithmetic(self) -> None:
        self.assertEqual(ec.N3, 708)
        self.assertEqual(ec.DELTA, 15)
        self.assertEqual(ec.RANK, 44)
        self.assertEqual(ec.TRACE_B, 60)
        self.assertEqual(ec.TRACE_C, 8)
        self.assertEqual(ec.EQUALITY_KERNEL_RANK, 36)

    def test_unique_trace_square_equality_rank(self) -> None:
        rows = ec.equality_rank_rows()
        minimizers = [
            row["nonzero_rank"]
            for row in rows
            if Fraction(str(row["combined_floor"])) == 8
        ]
        self.assertEqual(minimizers, [8])
        self.assertTrue(
            all(
                Fraction(str(row["combined_floor"])) >= 8
                for row in rows
            )
        )

    def test_integral_idempotent_orthogonal_split_certificate(self) -> None:
        certificate = ec.equality_split_certificate()
        split = certificate["integral_split"]
        self.assertEqual(split["image_rank"], 8)
        self.assertEqual(split["kernel_rank"], 36)
        self.assertTrue(split["canonical_idempotent_check"])
        self.assertIn("integral endomorphisms", split["integrality_gate"])
        self.assertIn("orthogonality", split["orthogonality_gate"].lower())

    def test_kernel_even_unimodular_obstruction(self) -> None:
        obstruction = ec.equality_split_certificate()["signature_obstruction"]
        self.assertEqual(obstruction["kernel_rank"], 36)
        self.assertEqual(obstruction["kernel_rank_mod_8"], 4)
        self.assertTrue(obstruction["van_der_blij_contradiction"])
        self.assertTrue(
            ec.signature_obstructs_even_unimodular(
                36,
                even=True,
                integral=True,
                unimodular=True,
                positive_definite=True,
            )
        )

    def test_S_evenness_is_derived_not_assumed_from_integrality(self) -> None:
        forms = ec.equality_split_certificate()["scaled_dual_forms"]
        self.assertEqual(forms["S_definition"], "S=21*G^-1")
        self.assertIn("21L* subset L", forms["S_integrality"])
        self.assertIn("21*S_ii", forms["S_evenness"])
        self.assertEqual(forms["global_product"], "S*Q=B")
        self.assertIn("S_K*Q_K=I_36", forms["kernel_product"])

    def test_trace_square_parity(self) -> None:
        certificate = ec.trace_square_parity_certificate()
        self.assertEqual(certificate["two_by_two_residue_matrices_checked"], 16)
        self.assertEqual(certificate["traceC_mod_2"], 0)
        self.assertEqual(certificate["traceC2_mod_2"], 0)

    def test_refined_trace_floors(self) -> None:
        data = ec.refined_trace_data()
        self.assertTrue(data["equality_excluded"])
        self.assertEqual(data["refined_traceC2_floor"], 10)
        self.assertEqual(data["refined_traceB2_floor"], 116)
        self.assertEqual(
            ec.RANK + 4 * ec.TRACE_C + 4 * data["refined_traceC2_floor"],
            116,
        )

    def test_strict_determinant_and_direct_mod_four_caps(self) -> None:
        data = ec.determinant_refinement()
        self.assertEqual(data["wave24_analytic_cap"], 6561)
        self.assertEqual(data["strict_analytic_result"], "det(B)<6561")
        self.assertEqual(data["largest_integer_below_6561"], 6560)
        self.assertEqual(data["detB_mod_4"], 1)
        self.assertEqual(data["direct_mod_four_cap"], 6557)
        self.assertEqual(data["factorized_congruence_cap"], 6525)

    def test_complete_h_and_detQ_enumeration(self) -> None:
        summary = ec.factor_pair_summary()
        self.assertEqual(summary["complete_pair_count"], 323)
        self.assertEqual(
            summary["h_values"],
            [9, 21, 49, 81, 189, 441, 729, 1029],
        )
        self.assertEqual(
            [row["detQ_count"] for row in summary["rows"]],
            [181, 77, 33, 19, 8, 3, 1, 1],
        )
        self.assertEqual(
            [row["detQ_max"] for row in summary["rows"]],
            [725, 309, 133, 77, 33, 13, 5, 5],
        )
        self.assertEqual(summary["combined_best_pair"]["h"], 9)
        self.assertEqual(summary["combined_best_pair"]["detQ"], 725)
        self.assertEqual(summary["combined_best_pair"]["detB"], 6525)

    def test_every_detQ_progression_is_exact(self) -> None:
        summary = ec.factor_pair_summary()
        for row in summary["rows"]:
            expected = list(range(5, row["detQ_max"] + 1, 4))
            self.assertEqual(row["detQ_values"], expected)
            self.assertTrue(all(value % 4 == 1 for value in expected))
            self.assertTrue(all(row["h"] * value < 6561 for value in expected))

    def test_independent_bruteforce_pair_set(self) -> None:
        expected: set[tuple[int, int, int]] = set()
        for exponent_3 in range(45):
            for exponent_7 in range(45):
                h = 3**exponent_3 * 7**exponent_7
                if h == 1 or h % 4 != 1 or h * 5 >= 6561:
                    continue
                for detq in range(5, (6560 // h) + 1):
                    if detq % 4 == 1:
                        expected.add((h, detq, h * detq))
        actual = {
            (row["h"], row["detQ"], row["detB"])
            for row in ec.enumerate_factor_pairs()
        }
        self.assertEqual(actual, expected)

    def test_false_global_S_equals_Q_inverse_control(self) -> None:
        survivor = ec.frozen_survivor_control()
        self.assertTrue(survivor["S_times_Q_equals_B"])
        self.assertFalse(survivor["S_times_Q_equals_identity"])
        self.assertTrue(survivor["false_global_statement_rejected"])
        self.assertIn("only", survivor["correct_scope"])

    def test_omitted_evenness_hostile_control(self) -> None:
        control = ec.omitted_evenness_control()
        self.assertTrue(control["C_integral_idempotent"])
        self.assertEqual(control["traceC"], 8)
        self.assertEqual(control["traceC2"], 8)
        self.assertEqual(control["detB"], 6561)
        self.assertTrue(control["S_times_G_equals_21I"])
        self.assertTrue(control["G_times_B_equals_21Q"])
        self.assertTrue(control["S_times_Q_equals_B"])
        self.assertFalse(control["G_even"])
        self.assertFalse(control["S_even"])
        self.assertFalse(control["Q_even"])
        self.assertFalse(control["signature_obstruction_available_from_S"])

    def test_nonintegral_idempotent_does_not_split_Z44(self) -> None:
        control = ec.nonintegral_idempotent_control()
        self.assertTrue(control["symmetric"])
        self.assertTrue(control["idempotent"])
        self.assertFalse(control["integral_endomorphism"])
        self.assertEqual(control["traceC"], "8/1")
        self.assertEqual(control["traceC2"], "8/1")
        self.assertEqual(control["index_of_integral_image_plus_kernel"], 256)
        self.assertFalse(control["integral_direct_sum"])

    def test_rank_divisible_by_eight_mutation(self) -> None:
        control = ec.divisible_rank_control()
        self.assertEqual(control["mutated_kernel_rank"], 32)
        self.assertEqual(control["mutated_kernel_rank_mod_8"], 0)
        self.assertFalse(control["signature_obstruction"])
        self.assertEqual(control["witness_rank"], 32)
        self.assertTrue(control["witness_even_integral"])
        self.assertTrue(control["witness_positive_definite"])
        self.assertEqual(control["witness_determinant"], 1)

    def test_congruence_omission_controls(self) -> None:
        controls = ec.congruence_and_cap_controls()
        self.assertEqual(controls["valid"]["pair_count"], 323)
        self.assertEqual(controls["valid"]["maximum"]["detB"], 6525)
        self.assertEqual(
            controls["omit_detQ_one_mod_four_but_keep_odd"]["maximum"]["detB"],
            6543,
        )
        self.assertEqual(
            controls["omit_all_detQ_parity_and_congruence"]["maximum"]["detB"],
            6552,
        )
        self.assertEqual(
            controls["omit_h_one_mod_four"]["maximum"]["detB"],
            6559,
        )
        self.assertIn(3, controls["omit_h_one_mod_four"]["extra_h_values"])
        self.assertIn(7, controls["omit_h_one_mod_four"]["extra_h_values"])

    def test_strict_cap_enumeration_hostile_boundary(self) -> None:
        control = ec.congruence_and_cap_controls()[
            "wrongly_allow_analytic_equality"
        ]
        equality_pairs = control["spurious_detB_6561_pairs"]
        self.assertEqual(control["maximum"]["detB"], 6561)
        self.assertEqual(
            [(row["h"], row["detQ"]) for row in equality_pairs],
            [(9, 729), (81, 81), (729, 9)],
        )

    def test_wave24_abstract_survivor_is_retained(self) -> None:
        survivor = ec.frozen_survivor_control()
        self.assertEqual(survivor["source_status"], "VERIFIED")
        self.assertEqual(survivor["h"], 9)
        self.assertEqual(survivor["detQ"], 9)
        self.assertEqual(survivor["detB"], 81)
        self.assertEqual(survivor["traceC2"], 32)
        boundary = survivor["semantic_boundary"]
        self.assertFalse(boundary["graph_realization_proved"])
        self.assertFalse(boundary["primitive_embedding_in_Z231_proved"])

    def test_build_result_status_wall(self) -> None:
        result = ec.build_results()
        conclusion = result["conclusion"]
        self.assertEqual(conclusion["conditional_traceC2_floor"], 10)
        self.assertEqual(conclusion["conditional_traceB2_floor"], 116)
        self.assertEqual(conclusion["conditional_combined_detB_cap"], 6525)
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


if __name__ == "__main__":
    unittest.main()
