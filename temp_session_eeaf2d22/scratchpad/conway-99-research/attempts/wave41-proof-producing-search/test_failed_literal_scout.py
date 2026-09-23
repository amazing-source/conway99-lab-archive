from __future__ import annotations

import importlib.util
import json
import sys
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).with_name("failed_literal_scout.py")
SPEC = importlib.util.spec_from_file_location(
    "wave41_failed_literal_scout", MODULE_PATH
)
assert SPEC is not None and SPEC.loader is not None
sys.path.insert(0, str(MODULE_PATH.parent))
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class FailedLiteralScoutTests(unittest.TestCase):
    def test_parse_variables(self) -> None:
        self.assertEqual(MODULE.parse_variables("13,175,188"), (13, 175, 188))

    def test_rejects_duplicate_variables(self) -> None:
        with self.assertRaises(Exception):
            MODULE.parse_variables("13,13")

    def test_archived_result_has_fail_closed_scope(self) -> None:
        path = MODULE_PATH.with_name("branch-15-failed-literal-scout.json")
        data = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(
            data["format"], "wave41-branch15-failed-literal-scout-v1"
        )
        self.assertEqual(data["result"]["endpoint_cases_closed"], 0)
        self.assertEqual(
            data["result"]["branch15_candidate_unsat_by_failed_literal"],
            bool(data["doubly_failed_variables"]),
        )
        self.assertEqual(
            data["source"]["path"],
            "attempts/wave37-proof-producing-endpoint/branch-15.opb.gz",
        )
        self.assertEqual(
            data["closure"]["path"],
            "attempts/wave41-proof-producing-search/"
            "branch-15-propagation-certificate.json",
        )
        for record in data["records"]:
            if record["contradiction"] is None:
                self.assertEqual(
                    record["status"],
                    "PROPAGATION_FIXED_POINT_NO_CONCLUSION",
                )


if __name__ == "__main__":
    unittest.main()
