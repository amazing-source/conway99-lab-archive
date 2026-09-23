#!/usr/bin/env python3
"""Hostile tests for the independent Wave 35 spectral verifier."""

from __future__ import annotations

import copy
import importlib.util
import sys
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("wave35_spectral_independent", HERE / "independent_check.py")
assert SPEC is not None and SPEC.loader is not None
check = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = check
SPEC.loader.exec_module(check)


class IndependentWave35Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.results = check.build_results()

    def test_endpoint_is_equality_not_generic_upper_bound(self) -> None:
        self.assertEqual(self.results["endpoint"]["q_per_triangle"], 12)
        with self.assertRaises(check.CheckFailure):
            check.endpoint_premises(4155)

    def test_snf_is_unique_under_frozen_inputs(self) -> None:
        self.assertEqual(
            self.results["smith_and_reflection"]["snf"],
            "diag(1^44,4^143,68^44)",
        )
        factors = [1] * 44 + [4] * 143 + [68] * 44
        check.validate_snf_factors(factors)
        wrong_two_adic = copy.copy(factors)
        wrong_two_adic[44] = 2
        with self.assertRaises(check.CheckFailure):
            check.validate_snf_factors(wrong_two_adic)
        wrong_chain = copy.copy(factors)
        wrong_chain[43] = 17
        with self.assertRaises(check.CheckFailure):
            check.validate_snf_factors(wrong_chain)

    def test_reflection_identity(self) -> None:
        result = self.results["smith_and_reflection"]
        self.assertEqual(result["C_identity"], "C^2=441I")
        self.assertEqual(result["C_spectrum"], {"+21": 44, "-21": 187})

    def test_all_forty_schur_triples_reconstructed(self) -> None:
        result = self.results["schur_and_compressions"]
        self.assertEqual(result["mixed_triple_count"], 40)
        self.assertEqual(result["mixed_negative_count"], 0)
        self.assertEqual(result["mixed_zero_count"], 15)
        self.assertEqual(result["mixed_smallest_positive"], "1/231")

    def test_support_compression_slack(self) -> None:
        result = self.results["schur_and_compressions"]
        self.assertEqual(result["B_projector_traces"]["0"], "-44")
        self.assertEqual(result["B_unallocated_slack"], "266112/25")

    def test_incidence_scalar_route_is_not_a_graph(self) -> None:
        result = self.results["incidence_frobenius"]
        self.assertEqual(result["per_row_square_range"], [492, 780])
        self.assertFalse(result["scalar_is_matrix_or_graph"])

    def test_local_scope_separates_actual_and_relaxed(self) -> None:
        result = self.results["local_controls"]
        self.assertTrue(result["adjacent_all_actual_cycle_types_positive"])
        self.assertEqual(result["nonadjacent_control_actual_incidence_realization"], "NOT_CLAIMED")

    def test_principal_degree_threshold_is_sharp(self) -> None:
        result = self.results["principal_minor"]
        self.assertEqual(result["gershgorin_positive_margin"], 1)
        self.assertFalse(result["condition_constructed"])
        self.assertTrue(result["degree_four_is_not_sufficient"])

    def test_absolute_algebraic_sum_is_not_the_condition(self) -> None:
        result = self.results["principal_minor"]
        self.assertEqual(result["hostile_switched_K5_support_degree"], 4)
        self.assertLessEqual(result["hostile_switched_K5_max_absolute_algebraic_sum"], 3)
        self.assertTrue(result["absolute_algebraic_row_sum_is_not_sufficient"])

    def test_status_wall(self) -> None:
        status = self.results["status"]
        self.assertFalse(status["endpoint_matrix_constructed"])
        self.assertFalse(status["endpoint_excluded"])
        self.assertFalse(status["upper_bound_improved_below_4158"])
        self.assertEqual(status["conway_99"], "UNKNOWN")


if __name__ == "__main__":
    unittest.main()
