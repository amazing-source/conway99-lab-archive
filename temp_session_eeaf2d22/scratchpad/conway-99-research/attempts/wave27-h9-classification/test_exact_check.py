#!/usr/bin/env python3
"""Tests for the Wave 27 h=9 classification counterexample."""

from __future__ import annotations

import json
import tempfile
import unittest
from fractions import Fraction
from pathlib import Path

import exact_check as check


class Wave27H9ClassificationChecks(unittest.TestCase):
    def test_frozen_inputs(self) -> None:
        frozen = check.verify_inputs()
        self.assertEqual(set(frozen), set(check.INPUTS))
        self.assertTrue(all(item["matches"] for item in frozen.values()))

    def test_root_cartan_data(self) -> None:
        self.assertEqual(check.determinant(check.A2), 3)
        self.assertEqual(check.determinant(check.E6), 3)
        self.assertEqual(check.determinant(check.E8), 1)
        self.assertTrue(check.positive_definite(check.E6))
        self.assertTrue(check.positive_definite(check.E8))

    def test_root_orbit_counts_and_components(self) -> None:
        result = check.root_component_check()
        self.assertEqual(result["root_counts"], {"A2": 6, "E6": 72, "E8": 240})
        self.assertEqual(result["candidate_root_count"], 1104)
        self.assertEqual(result["old_A2_survivor_root_count"], 1212)
        self.assertFalse(result["orthogonal_A2_summand"])

    def test_discriminant_modules_are_isometric(self) -> None:
        result = check.discriminant_module_check()
        self.assertEqual(result["group"], "(Z/3Z)^2")
        self.assertEqual(result["isometry_mod_3"], [[1, 1], [1, -1]])

    def test_e6_dual_minimum_is_complete(self) -> None:
        result = check.e6_dual_minimum()
        self.assertEqual(result["minimum"], "4/3")
        self.assertGreater(result["vectors_checked"], 0)

    def test_local_projector(self) -> None:
        package = check.local_e6_package()
        p = package["P"]
        self.assertEqual(check.matmul(p, p), p)
        self.assertEqual(check.trace(p), 1)
        self.assertEqual(check.rank(p), 1)
        self.assertEqual(package["projector_denominator"], Fraction(4, 3))

    def test_local_e6_package(self) -> None:
        result = check.verify_local_e6_package()
        self.assertEqual(result["trace_B"], 14)
        self.assertEqual(result["det_B"], 9)
        self.assertEqual(result["det_Q"], 3)
        self.assertEqual(result["trace_C_squared"], 16)
        self.assertTrue(result["Q_even_integral_positive_definite"])
        self.assertTrue(result["B_integral_and_identity_mod_two"])

    def test_local_e6_trace_floor(self) -> None:
        result = check.local_trace_floor_certificate()
        self.assertEqual(result["unrestricted_minimum"], 14)
        self.assertTrue(result["attained_by_explicit_Q6"])
        self.assertTrue(
            result["trace_10_gate"]["contradicts_det_B_at_least_9"]
        )

    def test_local_identities(self) -> None:
        package = check.local_e6_package()
        self.assertEqual(check.matmul(check.E6, package["Q"]), package["B"])
        self.assertEqual(
            check.matmul(package["G"], package["B"]),
            check.matscale(21, package["Q"]),
        )

    def test_full_dimensions_and_forms(self) -> None:
        package = check.full_package()
        self.assertTrue(all(len(matrix) == 44 for matrix in package.values()))
        for name in ("S", "Q", "G"):
            self.assertTrue(check.is_even_integral_form(package[name]), name)
            self.assertTrue(check.positive_definite(package[name]), name)

    def test_full_determinants(self) -> None:
        package = check.full_package()
        self.assertEqual(check.determinant(package["S"]), 9)
        self.assertEqual(check.determinant(package["Q"]), 9)
        self.assertEqual(check.determinant(package["B"]), 81)
        self.assertEqual(check.determinant(package["G"]), Fraction(21**44, 9))

    def test_full_coupled_identities(self) -> None:
        package = check.full_package()
        self.assertEqual(
            check.matmul(package["S"], package["G"]),
            check.matscale(21, check.identity(44)),
        )
        self.assertEqual(check.matmul(package["S"], package["Q"]), package["B"])
        self.assertEqual(
            check.matmul(package["G"], package["B"]),
            check.matscale(21, package["Q"]),
        )
        self.assertTrue(check.congruent_identity_mod_two(package["B"]))

    def test_full_trace_and_rank(self) -> None:
        result = check.verify_full_package()
        self.assertEqual(result["trace_B"], 60)
        self.assertEqual(result["trace_C"], 8)
        self.assertEqual(result["trace_C_squared"], 32)
        self.assertEqual(result["rank_C"], 2)

    def test_full_minimum_and_discriminant(self) -> None:
        result = check.verify_full_package()
        self.assertEqual(result["S_minimum"], 2)
        self.assertEqual(result["G_minimum"], 28)
        self.assertEqual(result["rank_mod_3_S"], 42)
        self.assertEqual(result["discriminant_group"], "(Z/3Z)^2")

    def test_deterministic_lf_json(self) -> None:
        expected = json.dumps(
            check.build_result(),
            indent=2,
            sort_keys=True,
        ) + "\n"
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "result.json"
            path.write_text(expected, encoding="utf-8", newline="\n")
            actual = path.read_bytes()
        self.assertEqual(actual, expected.encode("utf-8"))
        self.assertTrue(actual.endswith(b"\n"))
        self.assertNotIn(b"\r\n", actual)

    def test_scope_wall(self) -> None:
        result = check.build_result()["conclusions"]
        self.assertFalse(result["all_h9_forms_classified"])
        self.assertFalse(result["projector_or_Schur_origin_constructed"])
        self.assertFalse(result["n3_708_excluded"])
        self.assertEqual(result["Conway_99_status"], "UNKNOWN")
        self.assertEqual(result["novelty"], "UNKNOWN")


if __name__ == "__main__":
    unittest.main()
