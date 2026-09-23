from __future__ import annotations

import importlib.util
import json
import sys
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "wave112_independent", HERE / "independent_check.py"
)
assert SPEC and SPEC.loader
CHECK = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = CHECK
SPEC.loader.exec_module(CHECK)


class Wave112IndependentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = CHECK.build_results()

    def test_archived_result(self) -> None:
        archived = json.loads(
            (HERE / "independent-results.json").read_text(encoding="utf-8")
        )
        self.assertEqual(self.result, archived)

    def test_target_has_2079_induced_cycles(self) -> None:
        target = self.result["target"]
        self.assertEqual(target["nonedges"], 4158)
        self.assertTrue(target["common_pair_forced_nonadjacent"])
        self.assertEqual(target["induced_C4"], 2079)

    def test_h0_minima_are_21_20_18(self) -> None:
        minima = self.result["alternating_C4_minima"]
        self.assertEqual(minima["norm14_h0"], 21)
        self.assertEqual(minima["norm16_h0"], 20)
        self.assertEqual(minima["norm18_h0"], 18)

    def test_norm14_bound_is_exact_at_aggregate_level(self) -> None:
        rows = self.result["h0_codegree_audits"]["7"]["feasible_histograms"]
        self.assertEqual(
            rows,
            [{"codegree_0": 0, "codegree_1": 0, "codegree_2": 21}],
        )

    def test_h1_minimum_is_26(self) -> None:
        audit = self.result["norm18_h1_codegree_audit"]
        self.assertEqual(audit["pair_intersection_sum"], 62)
        self.assertEqual(audit["minimum_alternating_C4"], 26)
        minimizers = [
            row
            for row in audit["feasible_histograms"]
            if row["nonadjacent_codegree_2"] == 26
        ]
        self.assertEqual(len(minimizers), 1)
        self.assertEqual(minimizers[0]["adjacent_pair_codegree"], 1)

    def test_off_by_two_antipodal_rounding(self) -> None:
        audit = self.result["rank28_incidence"]
        self.assertEqual(audit["raw_pigeonhole_ceiling"], 51)
        self.assertTrue(audit["cycle_multiplicity_is_even_by_antipodes"])
        self.assertEqual(audit["forced_oriented_multiplicity"], 52)
        self.assertEqual(audit["forced_antipodal_support_pairs"], 26)

    def test_cap_25_is_only_sufficient(self) -> None:
        audit = self.result["rank28_incidence"]
        self.assertEqual(audit["incidence_upper_under_cap"], 103950)
        self.assertEqual(audit["oriented_incidence_lower"], 105624)
        self.assertEqual(audit["contradiction_margin"], 1674)
        self.assertFalse(self.result["status_wall"]["universal_cap_25_proved"])
        self.assertFalse(self.result["status_wall"]["rank28_excluded"])

    def test_fixed_cycle_partition(self) -> None:
        fixed = self.result["fixed_C4"]
        self.assertTrue(fixed["cross_edge_witnesses_distinct"])
        self.assertEqual(
            fixed["partition"],
            {
                "neither": 51,
                "p_only": 20,
                "n_only": 20,
                "one_p_and_one_n": 4,
            },
        )
        self.assertEqual(sum(fixed["partition"].values()), 95)

    def test_h0_remaining_selections(self) -> None:
        expected_neither = {"7": 1, "8": 2, "9": 3}
        for side, neither in expected_neither.items():
            row = self.result["h0_remaining_side_selections"][side]
            self.assertEqual(row["one_opposite_anchor"], 4)
            self.assertEqual(row["neither_opposite_anchor"], neither)
            self.assertEqual(
                row["one_opposite_anchor"] + row["neither_opposite_anchor"],
                row["total_remaining_on_side"],
            )

    def test_h1_signs_do_not_invalidate_count(self) -> None:
        hostile = self.result["hostile_checks"]
        self.assertTrue(hostile["h1_same_sign_edge_not_counted_as_alternating_cycle"])
        self.assertTrue(hostile["h1_signs_preserve_antipodal_pairing"])
        self.assertTrue(hostile["cycles_are_induced_not_merely_K22"])

    def test_global_status_fails_closed(self) -> None:
        wall = self.result["status_wall"]
        self.assertEqual(wall["Conway_99"], "UNKNOWN")
        self.assertEqual(wall["literature_novelty"], "UNKNOWN")


if __name__ == "__main__":
    unittest.main()
