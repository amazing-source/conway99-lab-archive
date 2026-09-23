from __future__ import annotations

import importlib.util
import json
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "wave43_rank28_comparison", HERE / "comparison_check.py"
)
assert SPEC is not None and SPEC.loader is not None
CHECK = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CHECK)
RESULT = json.loads((HERE / "comparison.json").read_text(encoding="utf-8"))


class Rank28ComparisonTests(unittest.TestCase):
    def test_comparison_schema(self) -> None:
        CHECK.validate(RESULT)

    def test_exact_agreement(self) -> None:
        self.assertEqual(RESULT["comparison_count"], 36)
        self.assertEqual(RESULT["discrepancy_count"], 0)
        self.assertEqual(RESULT["discrepancies"], [])
        self.assertTrue(all(check["match"] for check in RESULT["checks"]))

    def test_discovery_manifest(self) -> None:
        manifest = RESULT["discovery_even_package_manifest"]
        self.assertEqual(manifest["entries_checked"], 11)
        self.assertEqual(manifest["failures"], [])

    def test_scope_wall(self) -> None:
        wall = RESULT["status_wall"]
        self.assertEqual(wall["conditional_endpoint_rank_F7_floor"], 28)
        self.assertFalse(wall["endpoint_excluded"])
        self.assertFalse(wall["conway_99_resolved"])


if __name__ == "__main__":
    unittest.main()
