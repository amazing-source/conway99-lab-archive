from __future__ import annotations

import tempfile
import unittest
from fractions import Fraction
from pathlib import Path

import independent_check as check


class Wave25IndependentCheckTests(unittest.TestCase):
    def test_frozen_inputs_match_public_base(self) -> None:
        root = Path(__file__).resolve().parents[2]
        rows = check.verify_frozen_inputs(root)
        self.assertEqual(len(rows), 6)
        self.assertTrue(all(row["matches"] for row in rows.values()))

    def test_trace_square_floor_has_unique_equality_rank(self) -> None:
        result = check.equality_obstruction()
        self.assertEqual(result["old_trace_C2_floor"], 8)
        self.assertEqual(result["old_floor_unique_rank"], 8)
        self.assertEqual(result["equality_nonzero_spectrum"], {"1": 8})
        self.assertEqual(result["equality_zero_multiplicity"], 36)

    def test_integral_trace_square_parity(self) -> None:
        examples = [
            check.as_fraction_matrix(((1, 2), (3, 7))),
            check.as_fraction_matrix(((0, -5, 4), (2, 6, 1), (9, 0, -2))),
            check.diagonal([1] * 8 + [0] * 36),
        ]
        self.assertTrue(all(check.trace_square_parity(matrix) for matrix in examples))

    def test_rank_36_even_unimodular_signature_is_impossible(self) -> None:
        kernel = check.equality_obstruction()["kernel_block"]
        self.assertEqual(kernel["rank"], 36)
        self.assertFalse(kernel["even_unimodular_signature_gate_passes"])
        self.assertTrue(kernel["contradiction"])
        self.assertEqual(36 % 8, 4)

    def test_strict_trace_square_and_B_square_floors(self) -> None:
        result = check.equality_obstruction()
        self.assertEqual(result["strict_trace_C2_floor"], 10)
        self.assertEqual(result["strict_trace_B2_floor"], 116)

    def test_equality_control_is_rejected_only_after_evenness(self) -> None:
        control = check.equality_odd_control()
        self.assertEqual(control["trace_C"], 8)
        self.assertEqual(control["trace_C2"], 8)
        self.assertTrue(control["S_times_Q_equals_B"])
        self.assertFalse(control["global_S_equals_Q_inverse"])
        self.assertTrue(control["kernel_S0_equals_Q0_inverse"])
        self.assertFalse(control["Q_even"])
        self.assertFalse(control["S_even"])

    def test_global_scaled_dual_identity_is_not_kernel_identity(self) -> None:
        survivor = check.survivor_facts()
        self.assertTrue(survivor["S_times_Q_equals_B"])
        self.assertFalse(survivor["global_S_equals_Q_inverse"])
        self.assertFalse(survivor["global_S_times_Q_equals_identity"])
        self.assertEqual(survivor["global_identity_expected"], "S*Q=B, not I")

    def test_strict_and_congruence_caps(self) -> None:
        result = check.enumerate_determinant_index()
        self.assertEqual(result["analytic_cap"], 6561)
        self.assertTrue(result["analytic_equality_excluded"])
        self.assertEqual(result["strict_integer_cap"], 6560)
        self.assertEqual(result["strict_congruence_cap"], 6557)

    def test_exact_h_list_and_rank_bookkeeping(self) -> None:
        result = check.enumerate_determinant_index()
        self.assertEqual(
            result["h_values"],
            [9, 21, 49, 81, 189, 441, 729, 1029],
        )
        expected_ranks = {
            9: (42, 44),
            21: (43, 43),
            49: (44, 42),
            81: (40, 44),
            189: (41, 43),
            441: (42, 42),
            729: (38, 44),
            1029: (43, 41),
        }
        for row in result["rows"]:
            self.assertEqual(
                (row["rank_F3_M"], row["rank_F7_M"]),
                expected_ranks[row["h"]],
            )

    def test_exact_detQ_row_maxima(self) -> None:
        result = check.enumerate_determinant_index()
        actual = {row["h"]: row["detQ_max"] for row in result["rows"]}
        self.assertEqual(
            actual,
            {
                9: 725,
                21: 309,
                49: 133,
                81: 77,
                189: 33,
                441: 13,
                729: 5,
                1029: 5,
            },
        )

    def test_combined_cap_is_exactly_6525(self) -> None:
        result = check.enumerate_determinant_index()
        self.assertEqual(result["combined_exact_cap"], 6525)
        self.assertEqual(result["combined_maximizers"], [{"h": 9, "detQ": 725}])

    def test_each_hostile_relaxation_breaks_combined_cap(self) -> None:
        result = check.enumerate_determinant_index()
        controls = check.hostile_controls(result)
        for name in (
            "drop_strictness",
            "drop_h_not_one",
            "drop_h_mod_four",
            "drop_detQ_mod_four",
        ):
            with self.subTest(name=name):
                self.assertTrue(controls[name]["exceeds_combined_cap"])

    def test_h9_abstract_survivor_is_preserved(self) -> None:
        survivor = check.survivor_facts()
        self.assertEqual(survivor["det_S_h"], 9)
        self.assertEqual(survivor["det_Q"], 9)
        self.assertEqual(survivor["det_B"], 81)
        self.assertEqual(survivor["trace_B"], 60)
        self.assertEqual(survivor["trace_C"], 8)
        self.assertEqual(survivor["trace_C2"], 32)
        self.assertEqual(survivor["rank_C"], 2)

    def test_survivor_integrality_parity_and_bridges(self) -> None:
        survivor = check.survivor_facts()
        self.assertTrue(survivor["block_positive_definite"])
        self.assertTrue(survivor["S_even_integral_symmetric"])
        self.assertTrue(survivor["Q_even_integral_symmetric"])
        self.assertTrue(survivor["G_even_integral_symmetric"])
        self.assertTrue(survivor["S_times_G_equals_21I"])
        self.assertTrue(survivor["G_times_B_equals_21Q"])
        self.assertTrue(survivor["B_congruent_I_mod_2"])

    def test_survivor_remains_semantically_abstract(self) -> None:
        boundary = check.survivor_facts()["semantic_boundary"]
        self.assertTrue(boundary["abstract_coordinate_lattice_package"])
        self.assertFalse(boundary["primitive_embedding_in_Z231_proved"])
        self.assertFalse(boundary["projector_or_Hadamard_origin_proved"])
        self.assertFalse(boundary["Schur_square_origin_proved"])
        self.assertFalse(boundary["graph_realization_proved"])

    def test_matrix_helpers_reject_singular_inverse(self) -> None:
        with self.assertRaises(ValueError):
            check.inverse(check.as_fraction_matrix(((1, 2), (2, 4))))

    def test_generator_is_deterministic_LF_JSON(self) -> None:
        root = Path(__file__).resolve().parents[2]
        first = check.build_results(root)
        second = check.build_results(root)
        self.assertEqual(first, second)
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "result.json"
            payload = __import__("json").dumps(first, indent=2, sort_keys=True) + "\n"
            path.write_text(payload, encoding="utf-8", newline="\n")
            raw = path.read_bytes()
            self.assertTrue(raw.endswith(b"\n"))
            self.assertNotIn(b"\r\n", raw)

    def test_final_scope_does_not_exclude_n3_708(self) -> None:
        root = Path(__file__).resolve().parents[2]
        result = check.build_results(root)
        self.assertEqual(result["claim_label"], "VERIFIED")
        self.assertEqual(result["verdict"], "PASS_SCOPED_STRICTNESS")
        self.assertFalse(result["status_boundary"]["n3_708_excluded"])
        self.assertEqual(result["status_boundary"]["target_existence"], "UNKNOWN")
        self.assertEqual(result["status_boundary"]["novelty"], "UNKNOWN")


if __name__ == "__main__":
    unittest.main()
