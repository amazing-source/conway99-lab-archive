"""Focused tests for the Wave71 exact modular/theta checker."""

from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).with_name("exact_check.py")
SPEC = importlib.util.spec_from_file_location("wave71_exact_check", MODULE_PATH)
assert SPEC and SPEC.loader
CHECK = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CHECK)


class Wave71ExactCheckTests(unittest.TestCase):
    def test_eisenstein_reduction(self) -> None:
        self.assertEqual(
            CHECK.eisenstein_series(6, 14),
            [1] + [0] * 14,
        )
        self.assertEqual(
            CHECK.eisenstein_series(4, 9),
            [1, 2, 4, 0, 6, 0, 0, 2, 1, 2],
        )

    def test_all_required_theta_gaps_survive(self) -> None:
        for row in CHECK.modular_rows():
            self.assertTrue(row["required_gap_q1_through_q6_feasible_mod_7"])
            self.assertTrue(row["next_zero_condition_inconsistent"])

    def test_modular_upper_bounds(self) -> None:
        rows = CHECK.modular_rows()
        self.assertEqual(
            [row["q_discriminant_length_L"] for row in rows],
            list(range(2, 17, 2)),
        )
        self.assertEqual(
            [row["skoruppa_level_one_weight"] for row in rows],
            [148, 142, 136, 130, 124, 118, 112, 106],
        )
        self.assertEqual(
            [row["forced_upper_bound_min_K"] for row in rows],
            [28, 28, 28, 28, 28, 28, 28, 18],
        )
        self.assertEqual(rows[-1]["forced_upper_bound_min_L_dual"], "18/7")

    def test_q16_relation(self) -> None:
        relation = CHECK.q16_short_coefficient_relation()
        self.assertEqual(
            relation["eliminated_relation"],
            "A18 = 2 - A14 - A16 (mod 7)",
        )
        self.assertEqual(
            relation["parity_strengthening"],
            "A14 + A16 + A18 = 2 (mod 14)",
        )
        extremal = CHECK.theta_gap_system(106, 8, 9)
        coefficients = extremal["solution"]["particular"]
        self.assertEqual(coefficients, [2, 3, 1, 0, 0, 0, 0, 5, 4])
        self.assertEqual(
            CHECK.evaluate_coefficient(extremal["monomials"], coefficients, 9),
            2,
        )
        self.assertTrue(CHECK.theta_gap_system(106, 9, 9)["solution"]["inconsistent"])

    def test_profile_enumeration(self) -> None:
        self.assertEqual(
            [len(CHECK.integer_profiles(norm)) for norm in (14, 16, 18)],
            [3, 8, 8],
        )
        self.assertEqual(CHECK.subset_edge_bound_numerator(14), (287, 9))
        self.assertEqual(CHECK.subset_edge_bound_numerator(16), (344, 9))
        self.assertEqual(CHECK.subset_edge_bound_numerator(18), (45, 1))
        self.assertEqual(CHECK.subset_edge_bound_numerator(15), (35, 1))

    def test_low_norm_boundary(self) -> None:
        classification = CHECK.low_norm_classification()
        self.assertEqual(
            classification["post_coordinate_and_weight8_elimination"]["14"],
            ["seven +1 and seven -1"],
        )
        self.assertEqual(
            classification["signed_support_edge_bounds"]["16"]["surviving_h"],
            [0],
        )
        self.assertEqual(
            classification["norm14_forced_design"]["outside_incidence_design"],
            "2-(15,3,2) on 70 blocks",
        )
        self.assertEqual(
            classification["excluded_norm18_mixed_profile"][
                "forced_induced_edge_lower_bound"
            ],
            36,
        )

    def test_status_guards(self) -> None:
        result = CHECK.build_results()
        self.assertEqual(result["claim_label"], "DERIVED")
        self.assertFalse(result["endpoint"]["all_eight_rows_excluded"])
        self.assertEqual(result["endpoint"]["conway_status"], "UNKNOWN")
        self.assertEqual(result["endpoint"]["novelty"], "UNKNOWN")


if __name__ == "__main__":
    unittest.main()
