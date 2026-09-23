from __future__ import annotations

import importlib.util
import unittest
from fractions import Fraction
from pathlib import Path


MODULE = Path(__file__).with_name("independent_check.py")
SPEC = importlib.util.spec_from_file_location("wave96_verify", MODULE)
assert SPEC is not None and SPEC.loader is not None
VERIFY = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VERIFY)


class Wave96IndependentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = VERIFY.exact_result()

    def test_frozen_manifest(self) -> None:
        self.assertEqual(
            self.result["frozen_discovery_manifest_sha256"],
            "1d1e7d01edfbfcd2871683390b56e16dc36a18cfc899f301f15a0fce3b246a73",
        )

    def test_weighted_cap25(self) -> None:
        row = self.result["weighted_rank28"]
        self.assertEqual(row["weighted_lower"], 2_165_002)
        self.assertEqual(row["cap25_even_upper"], 2_115_382)
        self.assertTrue(row["cap25_contradicts"])
        self.assertFalse(row["cap25_proved"])

    def test_cap26_does_not_close_relaxation(self) -> None:
        row = self.result["weighted_rank28"]
        self.assertEqual(row["cap26_even_upper"], 2_199_996)
        self.assertFalse(row["cap26_contradicts"])

    def test_shell_cycle_minima(self) -> None:
        rows = self.result["weighted_rank28"]["shell_rows"]
        self.assertEqual(
            {
                key: value["minimum_alternating_C4"]
                for key, value in rows.items()
            },
            {"norm16_h0": 20, "norm18_h0": 18, "norm18_h1": 26},
        )

    def test_fixed_cycle_partition_is_only_a_reduction(self) -> None:
        row = self.result["fixed_C4"]
        self.assertEqual(row["outside_partition"], [51, 20, 20, 4])
        self.assertEqual(
            row["norm16_type_compatible_selections"], 6_148_477_125_000
        )
        self.assertFalse(row["graph_compatible_count_established"])

    def test_projector_inverse_and_interpolant(self) -> None:
        row = self.result["projector_relaxation"]
        self.assertEqual(
            row["projector_polynomial_values"],
            {"3": "0", "-4": "1", "14": "0"},
        )
        self.assertEqual(row["minimum_interpolant_squared_norm"], "28/5")
        self.assertEqual(row["residual_dimension"], 40)

    def test_cross_polytope_positive_control(self) -> None:
        row = self.result["projector_relaxation"]
        self.assertEqual(row["cross_polytope_size"], 80)
        self.assertEqual(
            row["cross_polytope_minimum_squared_distance"], "104/5"
        )
        self.assertGreater(Fraction(104, 5), 14)
        self.assertFalse(row["metric_relaxation_proves_cap25"])

    def test_norm20_profiles_are_exhaustive(self) -> None:
        row = self.result["norm20_dictionary"]
        self.assertEqual(len(row["profiles_after_parity_and_zero_sum"]), 6)
        self.assertEqual(
            row["surviving_profile"],
            {"plus_one": 10, "minus_one": 10, "other": 0},
        )

    def test_norm20_mixed_exclusions(self) -> None:
        row = self.result["norm20_dictionary"]["exclusions"]
        self.assertFalse(row["m3_neighbor_equation_feasible"])
        self.assertEqual(row["m2_same_forced_shared_neighbors"], 8)
        self.assertEqual(
            row["m2_mixed_plus2_unit_minimum_common_neighbors"], 3
        )
        self.assertEqual(
            row["m1_negative_neighborhood_intersection_minimum"], 3
        )
        self.assertTrue(row["all_mixed_profiles_excluded"])

    def test_norm20_c4_lower(self) -> None:
        row = self.result["norm20_dictionary"]
        self.assertEqual(row["same_edges_per_side_upper"], 3)
        self.assertEqual(
            [
                item["minimum_alternating_C4"]
                for item in row["alternating_C4_rows"]
            ],
            [15, 23, 31, 39],
        )
        self.assertEqual(row["universal_alternating_C4_lower"], 15)

    def test_rank30_cap24_is_only_sufficient(self) -> None:
        row = self.result["rank30_q14"]
        self.assertEqual(row["oriented_incidence_lower"], 102_630)
        self.assertEqual(row["forced_one_cycle_oriented_extensions"], 50)
        self.assertEqual(row["forced_one_cycle_antipodal_extensions"], 25)
        self.assertTrue(row["cap24_would_contradict"])
        self.assertFalse(row["cap24_proved"])

    def test_jacobi_boundary(self) -> None:
        row = self.result["jacobi_continuation"]
        self.assertTrue(row["common_index_principal_gram_checked"])
        self.assertFalse(row["transformation_law_established"])
        self.assertFalse(row["signed_coefficient_control_established"])
        self.assertEqual(row["route_status"], "UNKNOWN")

    def test_global_status_remains_unknown(self) -> None:
        row = self.result["status"]
        self.assertFalse(row["rank28_excluded"])
        self.assertFalse(row["rank30_excluded"])
        self.assertIsNone(row["N16_upper_bound"])
        self.assertIsNone(row["N18_upper_bound"])
        self.assertEqual(row["Conway_99"], "UNKNOWN")


if __name__ == "__main__":
    unittest.main()
