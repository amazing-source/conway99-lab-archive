from __future__ import annotations

import importlib.util
import json
import sys
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("wave112_exact", HERE / "exact_check.py")
assert SPEC and SPEC.loader
CHECK = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = CHECK
SPEC.loader.exec_module(CHECK)


class Wave112ExactTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = CHECK.build_results()

    def test_archived_result(self) -> None:
        archived = json.loads((HERE / "exact-results.json").read_text(encoding="utf-8"))
        self.assertEqual(self.result, archived)

    def test_target_four_cycle_count(self) -> None:
        self.assertEqual(CHECK.target_c4_count(), 2079)

    def test_regular_support_cycle_bounds(self) -> None:
        self.assertEqual(CHECK.regular_bipartite_c4_min(7), 21)
        self.assertEqual(CHECK.regular_bipartite_c4_min(8), 20)
        self.assertEqual(CHECK.regular_bipartite_c4_min(9), 18)

    def test_h1_cycle_bound(self) -> None:
        self.assertEqual(CHECK.norm18_h1_c4_min(), 26)

    def test_rank28_average_and_antipodal_rounding(self) -> None:
        row = self.result["rank28"]
        self.assertEqual(row["oriented_vector_C4_incidence_lower"], 105624)
        self.assertEqual(row["forced_some_C4_oriented_multiplicity"], 52)
        self.assertEqual(row["forced_some_C4_antipodal_supports"], 26)

    def test_cap_25_would_close_rank28(self) -> None:
        row = self.result["rank28"]
        self.assertEqual(row["sufficient_universal_cap_antipodal_supports"], 25)
        self.assertLess(
            row["incidence_upper_if_cap"],
            row["oriented_vector_C4_incidence_lower"],
        )

    def test_fixed_cycle_partition(self) -> None:
        self.assertEqual(
            CHECK.fixed_c4_partition(),
            {
                "neither": 51,
                "p_only": 20,
                "n_only": 20,
                "one_p_and_one_n": 4,
            },
        )

    def test_status_is_fail_closed(self) -> None:
        wall = self.result["status_wall"]
        self.assertFalse(wall["local_cap_25_proved"])
        self.assertFalse(wall["rank28_excluded"])
        self.assertEqual(wall["Conway_99"], "UNKNOWN")


if __name__ == "__main__":
    unittest.main()
