from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import check_witness as check  # noqa: E402
import transition_design as discovery  # noqa: E402


class Wave64ExactTests(unittest.TestCase):
    def test_independent_census(self) -> None:
        result = check.check_census()
        self.assertTrue(result["passed"])
        self.assertEqual(result["candidate_blocks"], 35_560)
        self.assertEqual(result["allowed_transitions"], 840)
        self.assertEqual(result["transition_triangle_count"], 280)

    def test_discovery_census(self) -> None:
        result = discovery.census()
        self.assertEqual(result["candidate_block_count"], 35_560)
        self.assertEqual(result["candidate_block_inclusion_exclusion"], 35_560)
        self.assertEqual(
            result["candidate_block_type_counts"],
            {
                "(0, 0, 3)": 6720,
                "(0, 1, 2)": 20160,
                "(0, 2, 1)": 6720,
                "(0, 3, 0)": 280,
                "(1, 0, 2)": 1680,
            },
        )
        self.assertEqual(set(result["transition_perfect_matching_count_per_base"]), {6040})

    def test_block_witness(self) -> None:
        result = check.check_block_witness(HERE / "block-witness.json")
        self.assertTrue(result["passed"])
        self.assertEqual(result["relation_counts_union_2_3_4"], [5, 74, 341])
        self.assertEqual(result["occupancy_n0_n1_n2"], [[32, 96, 12]] * 7)

    def test_fractional_control_independent(self) -> None:
        result = check.check_fractional()
        self.assertTrue(result["passed"])
        self.assertEqual(result["profile_residuals"], ["0"])
        self.assertEqual(result["transition_triangle_lhs"], "3/10")

    def test_fractional_control_discovery(self) -> None:
        result = discovery.check_fractional_control()
        self.assertTrue(result["passed"])
        self.assertEqual(result["endpoint_profile_residual_values"], ["0"])

    def test_reject_duplicate_block(self) -> None:
        payload = json.loads((HERE / "block-witness.json").read_text(encoding="utf-8"))
        payload["selected_blocks"][1]["index"] = payload["selected_blocks"][0]["index"]
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "bad.json"
            path.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaises(AssertionError):
                check.check_block_witness(path)

    def test_reject_changed_label(self) -> None:
        payload = json.loads((HERE / "block-witness.json").read_text(encoding="utf-8"))
        payload["selected_blocks"][0]["labels"][0][0] ^= 1
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "bad.json"
            path.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaises(AssertionError):
                check.check_block_witness(path)


if __name__ == "__main__":
    unittest.main()
