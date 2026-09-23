#!/usr/bin/env python3
"""Regression tests for the independent Wave 6 N3-count checker."""

from __future__ import annotations

import importlib.util
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path


ROOT = Path(__file__).resolve().parent
VERIFIER_PATH = ROOT / "n3-count-bound" / "verify.py"
SPEC = importlib.util.spec_from_file_location("n3_count_bound_verifier", VERIFIER_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("could not load the N3-count verifier")
VERIFIER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VERIFIER)


class N3CountBoundVerifierTests(unittest.TestCase):
    def test_committed_inputs_pass(self) -> None:
        output = StringIO()
        with redirect_stdout(output):
            self.assertEqual(VERIFIER.main([]), 0)
        rendered = output.getvalue()
        self.assertIn("PASS N3 count-bound exact checks", rendered)
        self.assertIn("global_n3_lower_bound 24", rendered)

    def test_abstract_extremal_checks(self) -> None:
        self.assertEqual(
            VERIFIER.abstract_small_edge_candidates(),
            [(18, (4,) * 9)],
        )
        self.assertEqual(VERIFIER.enumerate_m18_local_models(), 0)


if __name__ == "__main__":
    unittest.main()
