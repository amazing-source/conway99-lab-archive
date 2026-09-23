from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

import comparison_check as comparison


HERE = Path(__file__).resolve().parent


class PostFreezeComparisonTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = json.loads(
            (HERE / "comparison.json").read_text(encoding="utf-8")
        )

    def test_replay_agrees(self) -> None:
        self.assertEqual(comparison.compute(), self.result)

    def test_specified_discovery_sha(self) -> None:
        self.assertTrue(self.result["discovery_final_sha_verified"])
        self.assertEqual(
            self.result["comparison_input_hashes"][
                "attempts/wave41-evenpart-equality/exact-results.json"
            ],
            "8a9e58aaa1073ae4a87e183f904ce7f43eaa620bbac5a6f5d1f8445dd795dc85",
        )

    def test_mutated_discrepancy_is_rejected(self) -> None:
        mutated = copy.deepcopy(self.result)
        mutated["partition_comparison"]["6"]["canonical_targets"]["primary"] += 1
        with self.assertRaises(ValueError):
            comparison.validate(mutated)


if __name__ == "__main__":
    unittest.main()
