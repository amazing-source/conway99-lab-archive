from __future__ import annotations

import importlib.util
import json
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "wave130_independent_no_cache",
    HERE / "independent_no_cache_verify.py",
)
assert SPEC is not None and SPEC.loader is not None
VERIFY = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VERIFY)


class Wave130NoCacheTests(unittest.TestCase):
    def test_source_has_no_discovery_import_or_pickle(self) -> None:
        source = (HERE / "independent_no_cache_verify.py").read_text(encoding="utf-8")
        self.assertNotIn("import pickle", source)
        self.assertNotIn("importlib", source)
        self.assertNotIn("jacobi_lp", source)
        self.assertNotIn("exact_cdd_lp", source)

    def test_stored_verdict(self) -> None:
        result = json.loads(
            (HERE / "independent-results.json").read_text(encoding="utf-8")
        )
        self.assertEqual(result["claim_label"], "VERIFIED")
        self.assertEqual(
            result["cutoff_28"]["classification"],
            "VERIFIED_EXACT_RATIONAL_FEASIBLE",
        )
        self.assertEqual(result["cutoff_28"]["equalities_checked"], 454)
        self.assertEqual(result["cutoff_28"]["inequalities_checked"], 1686)
        self.assertEqual(result["cutoff_28"]["tight_inequalities"], 506)

    def test_status_wall(self) -> None:
        result = json.loads(
            (HERE / "independent-results.json").read_text(encoding="utf-8")
        )
        self.assertFalse(result["status_wall"]["rank28_realized"])
        self.assertFalse(result["status_wall"]["rank28_excluded"])
        self.assertEqual(result["status_wall"]["Conway_99"], "UNKNOWN")


if __name__ == "__main__":
    unittest.main()
