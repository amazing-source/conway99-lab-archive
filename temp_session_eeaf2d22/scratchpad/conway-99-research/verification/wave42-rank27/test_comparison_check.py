from __future__ import annotations

import copy
import importlib.util
import json
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "wave42_rank27_comparison", HERE / "comparison_check.py"
)
CHECK = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(CHECK)


class ComparisonTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = json.loads(
            (HERE / "comparison.json").read_text(encoding="utf-8")
        )

    def test_current_comparison_passes(self) -> None:
        CHECK.validate(self.result)

    def test_discrepancy_is_rejected(self) -> None:
        hostile = copy.deepcopy(self.result)
        hostile["discovery_independent_discrepancies"] = 1
        with self.assertRaises(ValueError):
            CHECK.validate(hostile)

    def test_hash_mismatch_is_rejected(self) -> None:
        hostile = copy.deepcopy(self.result)
        hostile["minimum_F_permutation_hash_matches"]["4+2"] = False
        with self.assertRaises(ValueError):
            CHECK.validate(hostile)


if __name__ == "__main__":
    unittest.main()
