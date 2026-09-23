#!/usr/bin/env python3
"""Premise-deletion and hostile controls for the Wave 30 verifier."""

from __future__ import annotations

import unittest

import independent_check as check


class Wave30GeneralHostileTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = check.build_result()
        cls.controls = cls.result["hostile_controls"]

    def test_every_named_hypothesis_deletion_fails_closed(self) -> None:
        full = set(check.ESSENTIAL_HYPOTHESES)
        for missing in check.ESSENTIAL_HYPOTHESES:
            with self.subTest(missing=missing):
                with self.assertRaises(check.MissingHypothesis):
                    check.build_result(full - {missing})

    def test_minimum_two_admits_a_mixed_row(self) -> None:
        control = self.controls["minimum_two"]
        self.assertEqual(sum(control["orthogonal_component_norms"]), 4)
        self.assertTrue(control["support_split_fails"])

    def test_rational_split_does_not_split_integral_rows(self) -> None:
        control = self.controls["rational_not_integral_split"]
        self.assertEqual(control["rootless_form"], "4*I_2")
        self.assertTrue(control["support_split_fails"])
        self.assertTrue(all("1/2" in item for item in control["projections"]))

    def test_detq_congruence_is_active(self) -> None:
        self.assertEqual(
            self.controls["drop_detQ_mod_four"][
                "additional_integer_candidates_under_bound"
            ],
            [6, 7, 8],
        )

    def test_trace_residue_is_active(self) -> None:
        control = self.controls["drop_trace_multiple_six"]
        self.assertEqual(control["trace_pair"], [28, 32])
        self.assertGreater(control["A_cap"], control["A_determinant"])
        self.assertTrue(control["contradiction_lost"])

    def test_integrality_is_active_in_log_cap(self) -> None:
        control = self.controls["drop_C_integrality"]
        self.assertEqual(control["traceC"], 6)
        self.assertGreater(
            control["det_I_plus_2C"],
            control["claimed_integral_cap"],
        )
        self.assertTrue(control["cap_violated"])

    def test_self_adjoint_real_spectrum_is_active(self) -> None:
        control = self.controls["drop_self_adjoint_real_spectrum"]
        self.assertEqual(control["nominal_cap"], 9)
        self.assertTrue(control["complex_eigenvalues"])
        self.assertIn("N^2", control["det_I_plus_2C"])

    def test_exceptional_cap_alone_is_insufficient(self) -> None:
        control = self.controls["use_only_A_cap"]
        self.assertEqual(control["survivor_count"], 6)
        self.assertIn([20, 2], control["types"])
        self.assertIn([20, 6], control["types"])

    def test_both_caps_without_equality_split_are_insufficient(self) -> None:
        control = self.controls["omit_equality_split"]
        self.assertEqual(control["survivor_count"], 5)
        self.assertEqual(
            {tuple(item) for item in control["types"]},
            {(4, 2), (12, 4), (20, 6), (28, 2), (36, 4)},
        )

    def test_evenness_is_active_in_signature_veto(self) -> None:
        control = self.controls["drop_evenness_in_equality_veto"]
        self.assertEqual(control["odd_unimodular_rank_two_control"], "I_2")
        self.assertTrue(control["signature_rank_veto_fails"])

    def test_wave29_type_is_excluded_strictly(self) -> None:
        item = check.classify(12, 6)
        self.assertEqual(item["detB_A"], 3645)
        self.assertEqual(item["A_logarithmic_data"]["detB_cap"], 729)
        self.assertEqual(
            item["obstruction"],
            "A_characteristic_pseudodeterminant_cap",
        )

    def test_no_discovery_module_is_imported(self) -> None:
        source = PathLike.read_independent_source()
        self.assertNotIn("import exact_check", source)
        self.assertNotIn("from exact_check", source)


class PathLike:
    """Tiny helper kept local so the hostile test has no discovery dependency."""

    @staticmethod
    def read_independent_source() -> str:
        with open(check.__file__, "r", encoding="utf-8") as stream:
            return stream.read()


if __name__ == "__main__":
    unittest.main()
