#!/usr/bin/env python3
"""Hostile and regression tests for the Wave 35 endpoint checker."""

from __future__ import annotations

import copy
import importlib.util
import sys
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("wave35_upper_exact", HERE / "exact_check.py")
assert SPEC is not None and SPEC.loader is not None
check = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = check
SPEC.loader.exec_module(check)


class EndpointChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.results = check.build_results()

    def test_endpoint_profile(self) -> None:
        self.assertEqual(
            self.results["signed_matrix"]["row_profile"],
            {"+1": 32, "-1": 36, "0": 162},
        )

    def test_q_mutation_rejected(self) -> None:
        with self.assertRaises(check.CheckError):
            check.endpoint_profile(11)

    def test_signed_polynomial_and_spectrum(self) -> None:
        signed = self.results["signed_matrix"]
        self.assertEqual(signed["identity"], "S^2=13S+68I")
        self.assertEqual(signed["spectrum"], {"17": 44, "-4": 187})

    def test_exact_smith_form(self) -> None:
        smith = self.results["smith_form_S"]
        self.assertEqual(smith["snf"], "diag(1^44,4^143,68^44)")
        self.assertEqual(smith["rank_F2_S"], 44)

    def test_smith_mutations_fail(self) -> None:
        factors = [1] * 44 + [4] * 143 + [68] * 44
        mutated = copy.copy(factors)
        mutated[44] = 2
        self.assertNotEqual(
            check.product(mutated),
            17**44 * 4**187,
        )
        mutated = copy.copy(factors)
        mutated[43] = 17
        self.assertFalse(all(
            right % left == 0 for left, right in zip(mutated, mutated[1:])
        ))

    def test_orthogonal_reflection(self) -> None:
        reflection = self.results["orthogonal_reflection"]
        self.assertEqual(reflection["identity"], "C^2=441I")
        self.assertEqual(reflection["row_sum"], -21)
        self.assertEqual(reflection["row_squared_norm"], 441)

    def test_schur_cube_is_positive_definite(self) -> None:
        powers = self.results["schur_power_collapse"]
        self.assertEqual(powers["cube"], "M^(o3)=M+60I is positive definite")
        self.assertEqual(
            powers["checks_1_through_9"]["3"]["eigen_on_ker_M"],
            60,
        )

    def test_all_mixed_schur_triples_survive(self) -> None:
        mixed = self.results["mixed_schur_endpoint"]
        self.assertEqual(mixed["triple_count"], 40)
        self.assertEqual(mixed["negative_count"], 0)

    def test_support_compression_has_slack(self) -> None:
        support = self.results["support_compression"]
        self.assertEqual(support["projector_traces"]["0"], "-44")
        self.assertEqual(support["unallocated_frobenius_slack"], "266112/25")

    def test_incidence_frobenius_control(self) -> None:
        incidence = self.results["incidence_support_bounds"]
        self.assertEqual(incidence["per_row_square_range"], [492, 780])
        self.assertEqual(
            incidence["scalar_energy_control"]["attained_value"],
            231 * 492,
        )
        self.assertFalse(incidence["scalar_energy_control"]["is_matrix_or_graph"])

    def test_adjacent_cycle_blocks_survive(self) -> None:
        adjacent = self.results["adjacent_vertex_blocks"]
        self.assertEqual(
            set(adjacent["cycle_partition_determinants"]),
            {"12", "8+4", "6+6", "4+4+4"},
        )
        self.assertTrue(all(
            value > 0 for value in adjacent["cycle_partition_determinants"].values()
        ))

    def test_nonadjacent_control_is_strict(self) -> None:
        control = self.results["nonadjacent_control_block"]
        self.assertEqual(control["frobenius_squared"], 13)
        self.assertEqual(control["row_sums"], [-2, -2, 1, 1, 1, 1, 1])
        self.assertEqual(control["column_sums"], [-2, -2, 1, 1, 1, 1, 1])

    def test_bareiss_rejects_nonsquare(self) -> None:
        with self.assertRaises(check.CheckError):
            check.determinant_bareiss([[1, 2], [3]])

    def test_principal_target_does_not_claim_construction(self) -> None:
        target = self.results["principal_minor_target"]
        self.assertEqual(target["status"], "TARGET_NOT_CONSTRUCTED")
        self.assertFalse(self.results["conclusion"]["endpoint_excluded"])


if __name__ == "__main__":
    unittest.main()
