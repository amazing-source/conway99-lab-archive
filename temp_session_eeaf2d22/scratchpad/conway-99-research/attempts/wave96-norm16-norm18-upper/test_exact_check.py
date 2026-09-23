from __future__ import annotations

import importlib.util
import unittest
from fractions import Fraction
from pathlib import Path


MODULE_PATH = Path(__file__).with_name("exact_check.py")
SPEC = importlib.util.spec_from_file_location("wave96_exact_check", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
CHECK = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CHECK)


class Wave96ExactTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = CHECK.exact_result()

    def test_weighted_target(self) -> None:
        row = self.result["weighted_rank28"]
        self.assertEqual(row["weighted_lower_value"], 2_165_002)
        self.assertEqual(row["induced_C4_count"], 2079)
        self.assertEqual(row["forced_support_C4_incidence_lower"], 53_195)
        self.assertEqual(row["forced_some_C4_antipodal_extensions"], 26)

    def test_cap25_is_sufficient_but_not_proved(self) -> None:
        row = self.result["weighted_rank28"]
        self.assertEqual(row["cap25_even_integer_weighted_upper"], 2_115_382)
        self.assertTrue(row["cap25_would_contradict"])
        self.assertFalse(row["cap26_would_contradict"])
        self.assertFalse(row["local_cap25_proved"])

    def test_fixed_cycle_partition_and_type_wall(self) -> None:
        fixed = self.result["fixed_C4"]
        self.assertEqual(
            fixed["outside_partition"],
            {"type00": 51, "P_only": 20, "N_only": 20, "type11": 4},
        )
        self.assertEqual(fixed["type_only_selection_count"], 6_148_477_125_000)
        self.assertTrue(fixed["type_only_count_is_not_graph_compatible_count"])

    def test_projector_inverse_and_interpolation(self) -> None:
        gram, inverse, minimum = CHECK.c4_projector()
        identity = [
            [
                sum(gram[i][k] * inverse[k][j] for k in range(4))
                for j in range(4)
            ]
            for i in range(4)
        ]
        self.assertEqual(
            identity,
            [[Fraction(i == j) for j in range(4)] for i in range(4)],
        )
        self.assertEqual(minimum, Fraction(28, 5))

    def test_cross_polytope_defeats_metric_cap(self) -> None:
        row = self.result["projector_relaxation"]
        self.assertEqual(row["cross_polytope_points_norm16"], 80)
        self.assertEqual(
            row["cross_polytope_minimum_squared_distance"], "104/5"
        )
        self.assertFalse(row["cap25_follows_from_projector_and_distance"])
        self.assertTrue(row["cross_polytope_is_not_lattice_or_graph"])

    def test_norm20_profile_enumeration(self) -> None:
        row = self.result["norm20_dictionary"]
        self.assertEqual(len(row["zero_sum_profiles_up_to_global_sign"]), 6)
        self.assertEqual(
            row["surviving_profile"],
            {"plus_one": 10, "minus_one": 10, "other": 0},
        )
        self.assertTrue(row["mixed_profiles_excluded"])

    def test_norm20_C4_rows(self) -> None:
        row = self.result["norm20_dictionary"]
        self.assertEqual(row["same_edges_per_side_upper"], 3)
        self.assertEqual(
            [item["minimum_alternating_C4"] for item in row["C4_rows"]],
            [15, 23, 31, 39],
        )
        self.assertEqual(row["universal_alternating_C4_lower"], 15)

    def test_rank30_target(self) -> None:
        row = self.result["rank30_q14"]
        self.assertEqual(row["oriented_support_C4_incidence_lower"], 102_630)
        self.assertEqual(row["forced_some_C4_oriented_extensions"], 50)
        self.assertEqual(row["forced_some_C4_antipodal_extensions"], 25)
        self.assertEqual(row["sufficient_universal_antipodal_cap"], 24)
        self.assertFalse(row["local_cap24_proved"])

    def test_status_boundary(self) -> None:
        status = self.result["status"]
        self.assertFalse(status["rank28_excluded"])
        self.assertFalse(status["rank30_excluded"])
        self.assertIsNone(status["N16_upper_bound"])
        self.assertIsNone(status["N18_upper_bound"])
        self.assertEqual(status["Conway_99"], "UNKNOWN")


if __name__ == "__main__":
    unittest.main()
