from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).with_name("exact_check.py")
SPEC = importlib.util.spec_from_file_location("wave176_exact_check", MODULE_PATH)
assert SPEC and SPEC.loader
CHECK = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CHECK)


class Wave176ExactCheckTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.data = CHECK.analyze()
        CHECK.verify(cls.data)

    def test_four_cycle_types_are_complete(self) -> None:
        self.assertEqual(
            set(self.data["adjacent_star_pair"]["cycle_types"]),
            {"6", "4+2", "3+3", "2+2+2"},
        )

    def test_adjacent_gram_ranks(self) -> None:
        types = self.data["adjacent_star_pair"]["cycle_types"]
        self.assertEqual(
            [types[name]["gram_rank"] for name in types], [10, 10, 8, 9]
        )

    def test_radical_dimension_bound(self) -> None:
        types = self.data["adjacent_star_pair"]["cycle_types"]
        self.assertEqual(types["3+3"]["span_rank_bounds"], [8, 9])
        self.assertEqual(types["2+2+2"]["span_rank_bounds"], [9, 10])

    def test_every_adjacent_type_has_a_cross_relation(self) -> None:
        for item in self.data["adjacent_star_pair"]["cycle_types"].values():
            self.assertGreaterEqual(
                item["cross_relation_quotient_dimension_lower"], 1
            )

    def test_exact_cross_coset_weights(self) -> None:
        types = self.data["adjacent_star_pair"]["cycle_types"]
        self.assertEqual(types["6"]["cross_coset"]["minimum_support"], 8)
        self.assertEqual(types["4+2"]["cross_coset"]["minimum_support"], 4)

    def test_nonadjacent_dimension_argument(self) -> None:
        nonadjacent = self.data["nonadjacent_star_pair"]
        self.assertEqual(nonadjacent["relation_dimension_lower"], 3)
        self.assertEqual(
            nonadjacent["cross_relation_quotient_dimension_lower"], 1
        )

    def test_trace_gram_rank_target(self) -> None:
        trace = self.data["trace_gram"]
        self.assertEqual(trace["rank_upper"], 65)
        self.assertEqual(trace["nonneighbor_average"], 7)

    def test_scope(self) -> None:
        self.assertIn("no endpoint exclusion", self.data["conclusion"])


if __name__ == "__main__":
    unittest.main()
