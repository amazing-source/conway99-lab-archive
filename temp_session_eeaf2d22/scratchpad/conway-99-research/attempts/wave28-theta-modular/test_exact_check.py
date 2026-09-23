#!/usr/bin/env python3
"""Hostile exact tests for the Wave 28 theta/modular arithmetic companion."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

import exact_check as check


class Wave28ThetaModularTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = check.build_result()

    def test_frozen_orchestrator_brief(self) -> None:
        self.assertEqual(
            self.result["frozen_inputs"][check.BRIEF_PATH],
            check.BRIEF_SHA256,
        )

    def test_discriminant_groups_and_exact_levels(self) -> None:
        rows = self.result["determinant_level_table"]
        self.assertEqual(
            {row["h"]: row["exact_level"] for row in rows},
            {9: 3, 21: 21, 49: 7, 81: 3, 189: 21, 441: 21, 729: 3, 1029: 21},
        )
        self.assertEqual(
            {row["h"]: row["theta_character"] for row in rows},
            {
                9: "TRIVIAL",
                21: "KRONECKER_CHI_21",
                49: "TRIVIAL",
                81: "TRIVIAL",
                189: "KRONECKER_CHI_21",
                441: "TRIVIAL",
                729: "TRIVIAL",
                1029: "KRONECKER_CHI_21",
            },
        )

    def test_scalar_sturm_bounds(self) -> None:
        self.assertEqual(check.sturm_bound(3), 7)
        self.assertEqual(check.sturm_bound(7), 14)
        self.assertEqual(check.sturm_bound(21), 58)

    def test_no_level_modular_self_duality(self) -> None:
        for row in self.result["determinant_level_table"]:
            self.assertTrue(row["level_modular_self_duality_impossible"])
            self.assertNotEqual(
                row["h"],
                int(row["determinant_required_for_level_modularity"]),
            )

    def test_fricke_partner_rootless_only_at_level_21(self) -> None:
        for row in self.result["determinant_level_table"]:
            self.assertEqual(
                row["fricke_partner_rootless_forced_by_min_G_ge_4"],
                row["exact_level"] == 21,
            )
            self.assertEqual(
                row["G_scaling_from_fricke_partner"],
                21 // row["exact_level"],
            )

    def test_component_scaled_duals(self) -> None:
        expected_determinants = {"A2": 3, "A6": 7, "A20": 21, "E6": 3, "E8": 1}
        for name, determinant in expected_determinants.items():
            self.assertEqual(
                self.result["component_checks"][name]["determinant"],
                determinant,
            )
            self.assertTrue(
                self.result["component_checks"][name][
                    "twenty_one_dual_even_integral"
                ]
            )

    def test_fresh_ADE_census(self) -> None:
        census = self.result["ADE_scalar_theta_hostile_controls"]
        self.assertEqual(census["total"], 17)
        self.assertEqual(
            {int(value): len(cases) for value, cases in census["by_determinant"].items()},
            {9: 2, 21: 2, 49: 1, 81: 2, 189: 3, 441: 2, 729: 4, 1029: 1},
        )

    def test_every_allowed_h_has_scalar_theta_hostile_control(self) -> None:
        census = self.result["ADE_scalar_theta_hostile_controls"]["by_determinant"]
        self.assertEqual({int(value) for value in census}, set(check.ALLOWED_H))
        for cases in census.values():
            for case in cases:
                self.assertEqual(case["rank"], 44)
                self.assertTrue(case["passes_frame_visible_r4_lower_bound_462"])
                self.assertGreaterEqual(
                    int(FractionString(case["scaled_dual_minimum"])),
                    4,
                )

    def test_selected_frame_shell_floor(self) -> None:
        frame = self.result["frame_visible_constraints"]
        self.assertEqual(frame["distinct_antipodal_pairs"], 231)
        self.assertEqual(frame["scalar_theta_norm_four_coefficient_floor"], 462)
        self.assertFalse(
            frame["ordinary_theta_detects_selected_orientation_or_cubic_moment"]
        )

    def test_h9_discriminant_nonuniqueness(self) -> None:
        witness = self.result["h9_discriminant_nonuniqueness"]
        self.assertEqual(witness["discriminant_module"], "(Z/3Z)^2")
        self.assertEqual(witness["E8_5_A2_2"]["r2"], 1212)
        self.assertEqual(witness["E8_4_E6_2"]["r2"], 1104)
        self.assertNotEqual(
            witness["E8_5_A2_2"]["r2"],
            witness["E8_4_E6_2"]["r2"],
        )

    def test_rootless_h729_hostile_control(self) -> None:
        hostile = self.result["rootless_h729_same_Weil_hostile_control"]
        self.assertEqual(hostile["S0"]["rank"], 44)
        self.assertEqual(hostile["S0"]["determinant"], 729)
        self.assertEqual(hostile["S0"]["minimum"], 4)
        self.assertEqual(hostile["S0"]["theta_q_coefficient_r2"], 0)
        self.assertGreaterEqual(hostile["S0"]["theta_q2_coefficient_r4"], 462)
        self.assertEqual(hostile["S1"]["theta_q_coefficient_r2"], 672)
        self.assertTrue(hostile["same_discriminant_form"]["isometric"])
        self.assertTrue(hostile["same_Weil_representation_different_root_count"])

    def test_rootless_hostile_gram_matrices_directly(self) -> None:
        self.assertEqual(check.determinant(check.K12), 729)
        self.assertEqual(check.determinant(check.KV32F), 1)
        self.assertEqual(check.enumerate_vectors_leq(check.K12, 2), [])
        self.assertEqual(check.enumerate_vectors_leq(check.KV32F, 2), [])
        self.assertTrue(check.integral_even(check.scale_matrix(check.inverse(check.K12), 3)))
        self.assertTrue(check.integral_even(check.inverse(check.KV32F)))

    def test_odd_harmonic_cancellation(self) -> None:
        for degree in (1, 3, 5, 7):
            for value in range(-9, 10):
                self.assertEqual(value**degree + (-value) ** degree, 0)

    def test_deterministic_json(self) -> None:
        first = check.canonical_json(check.build_result())
        second = check.canonical_json(check.build_result())
        self.assertEqual(first, second)
        json.loads(first)
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "result.json"
            output.write_text(first, encoding="utf-8", newline="\n")
            self.assertEqual(output.read_bytes(), first.encode("utf-8"))


def FractionString(value: str):
    """Parse the checker's canonical Fraction string for comparisons."""
    from fractions import Fraction

    return Fraction(value)


if __name__ == "__main__":
    unittest.main()
