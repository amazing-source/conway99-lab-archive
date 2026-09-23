from __future__ import annotations

import importlib.util
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "attempts/wave43-all-rank33-lifts/exact_check.py"
RESULT = ROOT / "attempts/wave43-all-rank33-lifts/exact-results.json"


def load_module():
    spec = importlib.util.spec_from_file_location("wave43_rank33", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class Rank33LiftTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.module = load_module()
        cls.result = json.loads(RESULT.read_text(encoding="utf-8"))

    def test_frozen_source_hash(self) -> None:
        source = ROOT / self.module.SOURCE_CODE
        self.assertEqual(
            self.module.sha256_bytes(source.read_bytes()),
            self.module.SOURCE_CODE_SHA256,
        )

    def test_all_rank33_masks_retained(self) -> None:
        self.assertEqual(self.result["rank33_lift_count"], 264)
        self.assertEqual(len(self.result["rank33_masks"]), 264)
        self.assertEqual(len(set(self.result["rank33_masks"])), 264)
        self.assertEqual(
            self.module.sha256_bytes(
                self.module.canonical_bytes(self.result["rank33_masks"])
            ),
            self.result["rank33_masks_sha256"],
        )

    def test_component_theorem_census(self) -> None:
        self.assertEqual(
            self.result["component_size_partition_distribution"],
            {"(12, 24)": 264},
        )
        self.assertEqual(
            self.result["component_fibre_balance_distribution"],
            {"((4, 4, 4), (8, 8, 8))": 264},
        )
        self.assertEqual(
            self.result["necessary_exclusions"]["excluded_union_count"], 0
        )

    def test_candidate_census_partition(self) -> None:
        expected = {
            "(118718, 49736, 45032)": 48,
            "(131908, 54560, 49328)": 48,
            "(132196, 54736, 49520)": 24,
            "(132250, 54560, 49328)": 48,
            "(132402, 54648, 49424)": 96,
        }
        self.assertEqual(self.result["candidate_census_distribution"], expected)
        self.assertEqual(sum(expected.values()), 264)

    def test_exact_structural_kernel(self) -> None:
        self.assertEqual(
            self.result["forced_gram_rank_mod_1000003_distribution"],
            {"33": 264},
        )
        for record in self.result["per_mask"]:
            self.assertEqual(record["forced_gram_rank_mod_1000003"], 33)
            self.assertEqual(record["structural_kernel_dimension"], 3)

    def test_per_mask_consistency(self) -> None:
        for record in self.result["per_mask"]:
            self.assertEqual(record["component_sizes"], [12, 24])
            self.assertEqual(
                record["component_fibre_balances"], [[4, 4, 4], [8, 8, 8]]
            )
            self.assertEqual(record["forced_gram_minimum"], 0)
            for component in record["component_moments"]:
                self.assertTrue(component["cauchy_equality"])
            self.assertGreater(
                record["candidate_census"]["after_mixed_BH_nonnegativity"], 0
            )

    def test_scope_wall(self) -> None:
        wall = self.result["status_wall"]
        self.assertEqual(wall["full_B_for_any_surviving_mask"], "UNKNOWN")
        self.assertEqual(wall["compatible_H"], "UNKNOWN")
        self.assertFalse(wall["endpoint_excluded"])
        self.assertFalse(wall["conway_99_resolved"])


if __name__ == "__main__":
    unittest.main()
