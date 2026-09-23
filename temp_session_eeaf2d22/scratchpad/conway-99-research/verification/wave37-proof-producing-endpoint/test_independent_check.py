#!/usr/bin/env python3
"""Tests for the independent Wave 37 branch-15 OPB audit."""

from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest


SPEC = importlib.util.spec_from_file_location(
    "wave37_opb_independent_check",
    Path(__file__).resolve().with_name("independent_check.py"),
)
assert SPEC is not None and SPEC.loader is not None
check = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(check)


class ProofProducingEndpointIndependentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = check.build_results()

    def test_formula_identity_and_scope(self) -> None:
        formula = self.result["formula"]
        self.assertEqual(formula["refined_branch"], 15)
        self.assertEqual(formula["parent_branch"], 4)
        self.assertEqual(formula["sha256"], check.EXPECTED_OPB_SHA)
        self.assertEqual(formula["constraint_count"], 574_615)
        self.assertFalse(formula["completed_graph_automorphism_assumed"])

    def test_syntax_and_semantics(self) -> None:
        self.assertEqual(self.result["syntax"]["status"], "PASS")
        semantics = self.result["semantic_reconstruction"]
        self.assertEqual(semantics["status"], "PASS")
        self.assertTrue(
            semantics["every_constraint_byte_identical_to_independent_reconstruction"]
        )
        self.assertEqual(
            sum(group["constraint_count"] for group in semantics["groups"].values()),
            574_615,
        )

    def test_compression_round_trip(self) -> None:
        compression = self.result["compression"]
        self.assertEqual(compression["compressed_sha256"], check.EXPECTED_GZIP_SHA)
        self.assertTrue(compression["round_trip_exact"])
        self.assertEqual(compression["gzip_mtime"], 0)
        self.assertEqual(compression["gzip_os_byte"], 255)

    def test_parser_is_not_a_solver_result(self) -> None:
        parser = self.result["exact_parser"]
        self.assertEqual(parser["result"], "PARSE_ACCEPTED")
        self.assertEqual(parser["exit_code"], 0)
        self.assertIn("no SAT or UNSAT", parser["interpretation"])

    def test_status_remains_unknown(self) -> None:
        conclusion = self.result["conclusion"]
        self.assertTrue(conclusion["formula_artifact_verified"])
        self.assertFalse(conclusion["satisfiability_decided"])
        self.assertFalse(conclusion["unsat_proof_present"])
        self.assertFalse(conclusion["sat_graph_present"])
        self.assertFalse(conclusion["endpoint_excluded"])
        self.assertEqual(conclusion["target_status"], "UNKNOWN")


if __name__ == "__main__":
    unittest.main()
