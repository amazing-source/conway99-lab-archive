#!/usr/bin/env python3
"""Hostile controls for the Wave 33 rooted-construction exact checker."""

from __future__ import annotations

import ast
import copy
import json
import subprocess
import sys
import tempfile
import unittest
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import exact_check as exact


CERTIFICATE_PATH = HERE / "partial-design-certificate.json"
RESULTS_PATH = HERE / "exact-results.json"


class ExactCheckerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.certificate = json.loads(
            CERTIFICATE_PATH.read_text(encoding="utf-8")
        )
        cls.results = json.loads(RESULTS_PATH.read_text(encoding="utf-8"))

    def test_frozen_inputs_match(self) -> None:
        self.assertEqual(exact.verify_frozen_inputs(), exact.FROZEN)

    def test_labeled_support_census(self) -> None:
        model = exact.build_model()
        self.assertEqual(len(model["support"]), 14)
        self.assertEqual(len(model["active"]), 70)
        self.assertEqual(len(model["zeros"]), 15)
        self.assertEqual(
            Counter(model["active_kind"].values()),
            Counter({"E": 28, "N": 42}),
        )

    def test_fixed_support_block(self) -> None:
        checked = exact.support_block_checks(exact.build_model())
        self.assertEqual(checked["support_support_block"], "PASS")
        self.assertEqual(checked["support_degrees"], [14] * 14)

    def test_linear_consequences(self) -> None:
        checked = exact.derive_linear_consequences(exact.build_model())
        self.assertEqual(checked["active_active_degree"], 9)
        self.assertEqual(checked["active_zero_degree"], 3)
        self.assertEqual(checked["zero_degree"], 14)
        self.assertEqual(checked["zero_zero_edges"], 0)
        self.assertEqual(checked["active_graph_edge_count"], 315)
        self.assertEqual(checked["active_zero_edge_count"], 210)

    def test_explicit_twofold_design(self) -> None:
        blocks = exact.simple_twofold_triple_design()
        self.assertEqual(len(blocks), len(set(blocks)))
        self.assertEqual(len(blocks), 70)
        pair_counts = Counter(
            pair
            for block in blocks
            for pair in exact.combinations(block, 2)
        )
        self.assertEqual(Counter(pair_counts.values()), Counter({2: 105}))

    def test_partial_certificate_exact_metrics(self) -> None:
        checked = exact.verify_partial_design_certificate(self.certificate)
        self.assertEqual(
            checked["classification"],
            "EXACT_HOSTILE_PARTIAL_OBJECT_NOT_A_GRAPH",
        )
        self.assertEqual(checked["simple_twofold_triple_design"], "PASS")
        self.assertEqual(checked["active_zero_edge_count"], 210)
        self.assertEqual(
            checked["zero_zero_common_neighbor_histogram"], {"2": 105}
        )
        self.assertEqual(checked["support_group_balance_squared_defect"], 10)
        self.assertEqual(checked["support_group_balance_violation_count"], 10)
        self.assertEqual(checked["support_group_balance_exact_group_count"], 9)
        self.assertFalse(checked["support_group_balance_pass"])

    def test_main_status_wall_remains_unknown(self) -> None:
        wall = self.results["status_wall"]
        self.assertEqual(wall["complete_graph_extension"], "UNKNOWN")
        self.assertEqual(wall["complete_domain_UNSAT_certificate"], "NONE")
        self.assertEqual(wall["full_rooted_endpoint"], "UNKNOWN")
        self.assertEqual(wall["n3_708"], "UNKNOWN")
        self.assertEqual(wall["Conway_99"], "UNKNOWN")
        self.assertEqual(wall["novelty"], "UNKNOWN")

    def test_rejects_self_promotion(self) -> None:
        hostile = copy.deepcopy(self.certificate)
        hostile["claim_label"] = "VERIFIED"
        with self.assertRaisesRegex(AssertionError, "remain CANDIDATE"):
            exact.verify_partial_design_certificate(hostile)

    def test_rejects_missing_record(self) -> None:
        hostile = copy.deepcopy(self.certificate)
        hostile["active_to_zero_triples"].pop()
        with self.assertRaisesRegex(AssertionError, "70 records"):
            exact.verify_partial_design_certificate(hostile)

    def test_rejects_duplicate_active_label(self) -> None:
        hostile = copy.deepcopy(self.certificate)
        hostile["active_to_zero_triples"][1]["active"] = (
            hostile["active_to_zero_triples"][0]["active"]
        )
        with self.assertRaisesRegex(AssertionError, "duplicate active"):
            exact.verify_partial_design_certificate(hostile)

    def test_rejects_duplicate_design_block(self) -> None:
        hostile = copy.deepcopy(self.certificate)
        hostile["active_to_zero_triples"][1]["zeros"] = list(
            hostile["active_to_zero_triples"][0]["zeros"]
        )
        with self.assertRaisesRegex(AssertionError, "design drifted"):
            exact.verify_partial_design_certificate(hostile)

    def test_rejects_invalid_zero_label(self) -> None:
        hostile = copy.deepcopy(self.certificate)
        hostile["active_to_zero_triples"][0]["zeros"][0] = "Z15"
        with self.assertRaisesRegex(AssertionError, "invalid Z triple"):
            exact.verify_partial_design_certificate(hostile)

    def test_exact_cli_replay_is_byte_identical(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "replay.json"
            subprocess.run(
                [
                    sys.executable,
                    str(HERE / "exact_check.py"),
                    "--partial-certificate",
                    str(CERTIFICATE_PATH),
                    "--output",
                    str(output),
                ],
                cwd=exact.REPO,
                check=True,
            )
            self.assertEqual(output.read_bytes(), RESULTS_PATH.read_bytes())

    def test_exact_checker_imports_only_standard_library(self) -> None:
        tree = ast.parse((HERE / "exact_check.py").read_text(encoding="utf-8"))
        imported_roots = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported_roots.update(
                    alias.name.split(".", 1)[0] for alias in node.names
                )
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported_roots.add(node.module.split(".", 1)[0])
        self.assertEqual(
            imported_roots,
            {
                "__future__",
                "argparse",
                "hashlib",
                "json",
                "collections",
                "itertools",
                "pathlib",
                "typing",
            },
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
