#!/usr/bin/env python3
"""Scope and reproducibility tests for the bounded full-block scout."""

from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
SPEC = importlib.util.spec_from_file_location(
    "wave40_full_block_scout", HERE / "full_block_scout.py"
)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("cannot load full_block_scout.py")
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class FullBlockScoutTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = MODULE.derive()

    def test_stored_result_matches(self) -> None:
        self.assertEqual(
            (HERE / "full-block-scout-results.json").read_bytes(),
            MODULE.exact.canonical_json(self.result),
        )

    def test_scope_remains_bounded(self) -> None:
        self.assertEqual(
            self.result["claim_label"], "BOUNDED_SCOUT_NON_EVIDENTIARY"
        )
        self.assertIn("not an exhaustion", self.result["interpretation"])
        self.assertEqual(self.result["samples_per_partition_type"], 512)

    def test_samples_respect_proved_floor(self) -> None:
        self.assertEqual(len(self.result["records"]), 11)
        self.assertTrue(
            all(
                record["minimum_sampled_rank_F7"]
                >= self.result["proved_floor_from_exact_census"]
                for record in self.result["records"]
            )
        )

    def test_aligned_rank_31_control_and_identity(self) -> None:
        control = self.result["aligned_positive_control"]
        self.assertEqual(control["core_component_sizes"], [6] * 6)
        self.assertEqual(control["core_laplacian_rank_F7"], 30)
        self.assertEqual(control["full_39_block_rank_F7"], 31)
        self.assertEqual(
            self.result["exact_block_rank_identity"]["identity"],
            "rank_F7(K_39)=1+rank_F7(3I_36-A_core)",
        )


if __name__ == "__main__":
    unittest.main()
