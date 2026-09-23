#!/usr/bin/env python3
"""Hostile-mutation tests for the Wave 57 clean-room verifier."""

from __future__ import annotations

import copy
import importlib.util
import json
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "wave57_independent_check", HERE / "independent_check.py"
)
assert SPEC and SPEC.loader
CHECK = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CHECK)


class Wave57IndependentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.discovery = json.loads(CHECK.DISCOVERY.read_text(encoding="utf-8"))
        cls.prior = json.loads(CHECK.PRIOR.read_text(encoding="utf-8"))
        cls.result = CHECK.run_checks(write_output=False)

    def test_baseline_is_refuted_in_part(self) -> None:
        self.assertEqual(self.result["claim_label"], "REFUTED")
        self.assertEqual(self.result["verdict"], "REFUTED_IN_PART")
        self.assertEqual(
            self.result["corrected_ledgers"]["full_project_prior_row_count"], 3
        )
        self.assertEqual(
            self.result["status_boundary"]["conway_99_status"], "UNKNOWN"
        )

    def test_quotient_mutation_rejected(self) -> None:
        bad = copy.deepcopy(self.discovery)
        bad["quotient_and_supported_sectors"]["quotient_matrix"][1][2] = 9
        with self.assertRaises(AssertionError):
            CHECK.verify_discovery_ledger(bad)

    def test_supported_dimension_mutation_rejected(self) -> None:
        bad = copy.deepcopy(self.discovery)
        bad["quotient_and_supported_sectors"]["supported_sector"][
            "dimension_each"
        ] = 3
        with self.assertRaises(AssertionError):
            CHECK.verify_discovery_ledger(bad)

    def test_projector_rank_mutation_rejected(self) -> None:
        bad = copy.deepcopy(self.discovery)
        bad["projectors_and_restrictions"]["ranks"]["E3"] = 53
        with self.assertRaises(AssertionError):
            CHECK.verify_discovery_ledger(bad)

    def test_multiplicity_box_mutation_rejected(self) -> None:
        bad = copy.deepcopy(self.discovery)
        bad["forced_Y_multiplicities"]["mult_Y_minus4"] = [8, 12]
        with self.assertRaises(AssertionError):
            CHECK.verify_discovery_ledger(bad)

    def test_triangle_mutation_rejected(self) -> None:
        bad = copy.deepcopy(self.discovery)
        bad["combinatorial_moments"]["Y_triangles"] = 31
        with self.assertRaises(AssertionError):
            CHECK.verify_discovery_ledger(bad)

    def test_four_cycle_range_mutation_rejected(self) -> None:
        bad = copy.deepcopy(self.discovery)
        bad["multiplicity_fourth_moment_ledger"][0]["C4_X_max"] = 88
        with self.assertRaises(AssertionError):
            CHECK.verify_discovery_ledger(bad)

    def test_scalar_power_sum_mutation_rejected(self) -> None:
        bad = copy.deepcopy(self.discovery)
        bad["scalar_algebraic_integer_controls"][0][
            "residual_power_sums_p0_to_p4"
        ][4] += 1
        with self.assertRaises(AssertionError):
            CHECK.verify_controls(bad)

    def test_quadratic_factor_mutation_rejected(self) -> None:
        bad = copy.deepcopy(self.discovery)
        target = next(
            row for row in bad["scalar_algebraic_integer_controls"]
            if (row["a_mult_Y_3"], row["b_mult_Y_minus4"]) == (20, 8)
        )
        target["quadratic_factor"] = "(x^2-(-4)x+(2))^4"
        with self.assertRaises(AssertionError):
            CHECK.verify_controls(bad)

    def test_prior_multiplicity_mutation_rejected(self) -> None:
        bad = copy.deepcopy(self.prior)
        bad["general_checks"]["spectral_transfer_samples"]["2"][
            "kernel_multiplicities"
        ]["-4"] = 10
        with self.assertRaises(AssertionError):
            CHECK.prior_wave36_checks(bad)

    def test_star_order_mutation_rejected(self) -> None:
        bad = copy.deepcopy(self.discovery)
        bad["star_complement_reduction"]["Y_only_exact_rank_problem"][
            "lambda_3_star_complement_orders"
        ] = [39, 42]
        with self.assertRaises(AssertionError):
            CHECK.verify_discovery_ledger(bad)

    def test_status_inflation_rejected(self) -> None:
        bad = copy.deepcopy(self.discovery)
        bad["conclusion"]["conway_99_status"] = "VERIFIED"
        with self.assertRaises(AssertionError):
            CHECK.verify_discovery_ledger(bad)


if __name__ == "__main__":
    unittest.main()
