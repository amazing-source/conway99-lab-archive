#!/usr/bin/env python3
"""Tests for the small independent DRUP checker."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from check_drup import check_proof


CNF = """p cnf 2 4
1 2 0
1 -2 0
-1 2 0
-1 -2 0
"""


class DrupCheckerTests(unittest.TestCase):
    def test_two_rup_steps_prove_unsat(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            cnf = Path(directory) / "input.cnf"
            proof = Path(directory) / "proof.drup"
            cnf.write_text(CNF, encoding="ascii")
            proof.write_text("1 0\n0\n", encoding="ascii")
            report = check_proof(cnf, proof)
            self.assertTrue(report["valid"], report)
            self.assertEqual(report["empty_clause_step"], 2)

    def test_unjustified_empty_clause_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            cnf = Path(directory) / "input.cnf"
            proof = Path(directory) / "proof.drup"
            cnf.write_text(CNF, encoding="ascii")
            proof.write_text("0\n", encoding="ascii")
            report = check_proof(cnf, proof)
            self.assertFalse(report["valid"])
            self.assertEqual(report["reason"], "non-RUP addition")


if __name__ == "__main__":
    unittest.main()
