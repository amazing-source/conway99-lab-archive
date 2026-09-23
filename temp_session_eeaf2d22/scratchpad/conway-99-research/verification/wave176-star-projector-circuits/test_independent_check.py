from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


MODULE = Path(__file__).with_name("independent_check.py")
SPEC = importlib.util.spec_from_file_location("wave176_independent", MODULE)
assert SPEC and SPEC.loader
CHECK = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CHECK)


class IndependentWave176Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = CHECK.analyze()

    def test_star_simplex(self) -> None:
        self.assertEqual(self.result["star"]["gram_rank"], 6)
        self.assertTrue(
            self.result["star"]["projector_action_mod_relation"]
        )

    def test_trace_zero_target(self) -> None:
        self.assertEqual(self.result["trace_space"]["trace_zero_dimension"], 65)

    def test_integer_counts(self) -> None:
        self.assertEqual(
            self.result["integer_BLBt"],
            {
                "diagonal": 0,
                "edge_entry": 12,
                "row_sum": 756,
                "nonneighbor_sum": 588,
                "nonneighbor_average": 7,
            },
        )

    def test_four_direct_ranks(self) -> None:
        cycles = self.result["cycles"]
        self.assertEqual(
            [cycles[name]["gram_rank"] for name in cycles], [10, 10, 8, 9]
        )

    def test_radical_bounds(self) -> None:
        cycles = self.result["cycles"]
        self.assertEqual(cycles["3+3"]["possible_span_ranks"], [8, 9])
        self.assertEqual(cycles["2+2+2"]["possible_span_ranks"], [9, 10])

    def test_true_cross_relation_bounds(self) -> None:
        for item in self.result["cycles"].values():
            self.assertGreaterEqual(item["cross_quotient_dimension_lower"], 1)

    def test_rank_ten_supports(self) -> None:
        cycles = self.result["cycles"]
        self.assertEqual(cycles["6"]["support"]["minimum_support"], 8)
        self.assertEqual(cycles["4+2"]["support"]["minimum_support"], 4)

    def test_no_degenerate_kernel_promotion(self) -> None:
        cycles = self.result["cycles"]
        self.assertNotIn("support", cycles["3+3"])
        self.assertNotIn("support", cycles["2+2+2"])


if __name__ == "__main__":
    unittest.main()
