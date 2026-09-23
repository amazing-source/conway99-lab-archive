import json
import unittest
from pathlib import Path

import independent_verify as verify


HERE = Path(__file__).resolve().parent


class IndependentWave136Tests(unittest.TestCase):
    def test_character_matrix(self):
        self.assertEqual(
            verify.character_matrix(),
            [
                [1, 1, 1, 1],
                [1, 1, -1, -1],
                [1, -1, 1, -1],
                [1, -1, -1, 1],
            ],
        )

    def test_binary_macwilliams_and_arf(self):
        result = verify.binary_arf_checks(verify.DEFAULT_WITNESS)
        self.assertTrue(all(result["checks"].values()))
        self.assertEqual(result["forward_failure_weights"], [])
        self.assertEqual(result["inverse_failure_weights"], [])

    def test_gf4_counts_and_controls(self):
        result = verify.gf4_checks()
        self.assertEqual(result["raw_states"], 5050)
        self.assertEqual(result["allowed_even_nY_states"], 2550)
        self.assertEqual(result["forced_odd_nY_zero_states"], 2500)
        self.assertEqual(
            result["small_graph_controls"]
            ["graphs_checked_exhaustively_through_order"],
            4,
        )

    def test_support_three_table(self):
        table = {
            row["input_type"]: row
            for row in verify.support_three_table()
        }
        self.assertEqual(table["triangle"]["count"], 231)
        self.assertEqual(
            (table["induced_path"]["nY"], table["induced_path"]["nR"]),
            (2, 33),
        )
        self.assertEqual(
            sum(row["count"] for row in table.values() if row["input_type"]
                not in {"one_vertex", "edge", "nonedge"}),
            156849,
        )

    def test_sealed_results(self):
        expected = json.loads(
            (HERE / "independent-results.json").read_text(encoding="utf-8")
        )
        self.assertEqual(
            verify.build_results(verify.DEFAULT_WITNESS),
            expected,
        )


if __name__ == "__main__":
    unittest.main()
