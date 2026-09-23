#!/usr/bin/env python3
"""Focused regression tests for the independent Wave146 verifier."""

from __future__ import annotations

import copy
import importlib.util
import json
import sys
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "wave146_independent_verify", HERE / "independent_verify.py"
)
assert SPEC is not None and SPEC.loader is not None
VERIFY = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = VERIFY
SPEC.loader.exec_module(VERIFY)


class IndependentWave146Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.payload = json.loads(VERIFY.DISCOVERY_RESULT.read_text(encoding="utf-8"))

    def test_exact_certificate(self) -> None:
        result = VERIFY.replay(copy.deepcopy(self.payload))
        self.assertEqual(result["verdict"], "PASS_RATIONAL_RELAXATION")
        self.assertEqual(result["equalities_replayed"], 8981)
        self.assertEqual(result["root_filter_vs_direct_seven_graph_checks"], 3968)

    def test_mutated_coordinate_is_rejected(self) -> None:
        bad = copy.deepcopy(self.payload)
        bad["candidate"]["support"][0]["numerator"] += 1
        with self.assertRaises(AssertionError):
            VERIFY.replay(bad)

    def test_root_filter_equivalence_and_removed_cells(self) -> None:
        structure = VERIFY.build_structure()
        self.assertEqual(structure["equivalence_checks"], 62 * 64)
        self.assertEqual(len(structure["affected"]), 16)
        self.assertEqual(sum(map(len, structure["affected"].values())), 25)


if __name__ == "__main__":
    unittest.main()
