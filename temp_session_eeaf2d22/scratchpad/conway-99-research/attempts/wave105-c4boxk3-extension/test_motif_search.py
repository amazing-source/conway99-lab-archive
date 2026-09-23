from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).with_name("motif_search.py")
SPEC = importlib.util.spec_from_file_location("wave105_motif_search", MODULE_PATH)
assert SPEC and SPEC.loader
SEARCH = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = SEARCH
SPEC.loader.exec_module(SEARCH)


class Wave105MotifTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.summary = SEARCH.necessary_summary()

    def test_motif(self) -> None:
        motif = self.summary["motif"]
        self.assertEqual(motif["vertices"], 12)
        self.assertEqual(motif["edges"], 24)
        self.assertEqual(motif["internal_degree"], [4])

    def test_forced_outside_patterns(self) -> None:
        outside = self.summary["forced_outside_incidence"]
        self.assertEqual(outside["type_counts"], {"X0": 3, "X1": 48, "X2": 36})
        self.assertEqual(outside["incidences"], 120)
        self.assertEqual(outside["pair_incidences"], 36)
        self.assertTrue(outside["pattern_gram_matches_block_equation"])

    def test_outside_edge_rows(self) -> None:
        rows = self.summary["outside_edges"]["type_counts_by_t_eX0"]
        self.assertEqual(
            rows["0"],
            {"00": 0, "01": 12, "02": 30, "11": 156, "12": 300, "22": 51},
        )
        self.assertEqual(
            rows["3"],
            {"00": 3, "01": 0, "02": 36, "11": 168, "12": 288, "22": 54},
        )
        self.assertTrue(
            all(sum(row.values()) == 549 for row in rows.values())
        )

    def test_moment_census(self) -> None:
        moments = self.summary["outside_degree_moments"]
        self.assertEqual(
            moments["moment_row_counts_by_t"],
            {"0": 18, "1": 11, "2": 5, "3": 1},
        )
        self.assertEqual(
            moments["six_type_graphical_counts_by_t"],
            {"0": 18, "1": 11, "2": 4, "3": 1},
        )

    def test_single_graphical_rejection_is_x0_x1(self) -> None:
        rows = self.summary["outside_degree_moments"]["rows_by_t"]["2"]
        rejected = [row for row in rows if not row["all_six_type_graphical"]]
        self.assertEqual(len(rejected), 1)
        self.assertEqual(
            rejected[0]["six_type_graphical_tests"],
            [True, False, True, True, True, True],
        )

    def test_full_candidate_checker_rejects_empty_graph(self) -> None:
        with self.assertRaises(AssertionError):
            SEARCH.verify_full_adjacency([[0] * 99 for _ in range(99)])

    def test_linear_witness(self) -> None:
        witness_path = Path(__file__).with_name("linear-witness.json")
        witness = SEARCH.json.loads(witness_path.read_text(encoding="utf-8"))
        self.assertEqual(witness["outside_edges"], 549)
        self.assertTrue(witness["direct_linear_check"])
        outside = [[0] * 87 for _ in range(87)]
        for row, neighbors in enumerate(witness["adjacency_lists"]):
            for column in neighbors:
                outside[row][column] = 1
        SEARCH.verify_linear_outside(outside)

    def test_status_is_fail_closed(self) -> None:
        status = self.summary["status_wall"]
        self.assertEqual(status["linear_extension"], "FEASIBLE")
        self.assertEqual(status["full_common_neighbor_extension"], "UNKNOWN")
        self.assertFalse(status["motif_excluded"])
        self.assertEqual(status["Conway_99"], "UNKNOWN")


if __name__ == "__main__":
    unittest.main()
