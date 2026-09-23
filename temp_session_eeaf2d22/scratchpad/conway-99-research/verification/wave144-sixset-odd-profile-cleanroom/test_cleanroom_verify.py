#!/usr/bin/env python3
"""Regression and hostile-mutation tests for the clean-room Wave144 verifier."""

from __future__ import annotations

import copy
import importlib.util
import json
import sys
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "wave144_cleanroom_verify",
    HERE / "cleanroom_verify.py",
)
assert SPEC is not None and SPEC.loader is not None
VERIFY = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = VERIFY
SPEC.loader.exec_module(VERIFY)


class CleanroomVerifierTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.payload = json.loads(VERIFY.DISCOVERY_RESULTS.read_text(encoding="utf-8"))

    def test_full_certificate(self) -> None:
        result = VERIFY.verify(copy.deepcopy(self.payload))
        self.assertEqual(result["verdict"], "PASS_NULL_BOUNDARY")
        self.assertEqual(result["published_local_witnesses_replayed"], 66)
        self.assertEqual(result["aggregate_nonzero_integer_cells_replayed"], 65)
        self.assertEqual(result["graph_realization"], "NOT_ESTABLISHED")

    def test_mutated_local_witness_rejected(self) -> None:
        bad = copy.deepcopy(self.payload)
        witness = bad["selected_local_integer_witnesses"][0]
        first_key = next(iter(witness["z_by_subset_mask_sparse"]))
        witness["z_by_subset_mask_sparse"][first_key] += 1
        with self.assertRaises(AssertionError):
            VERIFY.verify(bad)

    def test_mutated_endpoint_cell_rejected(self) -> None:
        bad = copy.deepcopy(self.payload)
        bad["aggregate_endpoint_certificate"]["nonzero_cells"][0]["count"] += 1
        with self.assertRaises(AssertionError):
            VERIFY.verify(bad)

    def test_duplicate_or_missing_local_key_rejected(self) -> None:
        bad = copy.deepcopy(self.payload)
        bad["selected_local_integer_witnesses"].pop()
        with self.assertRaises(AssertionError):
            VERIFY.verify(bad)

    def test_class36_gap_is_reproduced(self) -> None:
        six_map, _ = VERIFY.independent_six_alignment()
        mask = VERIFY.graph_classes(6)[six_map[35]]
        support, _, stats = VERIFY.enumerate_support(
            mask, reverse=True, target_only=68
        )
        self.assertEqual(support, [])
        self.assertFalse(stats["target_found"])


if __name__ == "__main__":
    unittest.main()
