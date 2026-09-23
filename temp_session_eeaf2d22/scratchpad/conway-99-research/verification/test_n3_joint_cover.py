#!/usr/bin/env python3
"""Regression tests for the standalone N3 joint-cover verifier."""

from __future__ import annotations

import importlib.util
import json
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory


ROOT = Path(__file__).resolve().parent
VERIFIER_PATH = ROOT / "n3-joint-cover" / "verify.py"
CERTIFICATE_PATH = ROOT / "n3-joint-cover" / "n3-joint-cover.json"

SPEC = importlib.util.spec_from_file_location("n3_joint_cover_verifier", VERIFIER_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("could not load the N3 joint-cover verifier")
VERIFIER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VERIFIER)


class N3JointCoverVerifierTests(unittest.TestCase):
    def verify_mutation(self, mutation: object, message: str) -> None:
        with TemporaryDirectory() as directory:
            path = Path(directory) / "mutant.json"
            path.write_text(
                json.dumps(mutation, indent=2) + "\n",
                encoding="utf-8",
                newline="\n",
            )
            with self.assertRaisesRegex(ValueError, message):
                VERIFIER.verify(path)

    def test_committed_certificate_passes_by_default_and_explicit_path(self) -> None:
        for arguments in ([], [str(CERTIFICATE_PATH)]):
            with self.subTest(arguments=arguments):
                output = StringIO()
                with redirect_stdout(output):
                    self.assertEqual(VERIFIER.main(arguments), 0)
                self.assertIn("PASS N3 joint 12-branch cover", output.getvalue())

    def test_boolean_cannot_impersonate_top_level_integer(self) -> None:
        certificate = json.loads(CERTIFICATE_PATH.read_text(encoding="utf-8"))
        certificate["fixed_endpoint_edge"][0] = False
        self.verify_mutation(certificate, "fixed_endpoint_edge")

    def test_boolean_cannot_impersonate_branch_integer(self) -> None:
        certificate = json.loads(CERTIFICATE_PATH.read_text(encoding="utf-8"))
        certificate["branches"][0]["branch"] = True
        self.verify_mutation(certificate, "branch must be an integer")

    def test_boolean_cannot_impersonate_literal_integer(self) -> None:
        certificate = json.loads(CERTIFICATE_PATH.read_text(encoding="utf-8"))
        certificate["branches"][0]["positive_edge_literals"][0] = True
        self.verify_mutation(certificate, "positive_edge_literals")

    def test_nonstandard_json_constant_and_duplicate_key_are_rejected(self) -> None:
        original = CERTIFICATE_PATH.read_text(encoding="utf-8")
        mutations = (
            (original.replace('"pair_count": 7', '"pair_count": NaN', 1), "constant"),
            (original.replace("{", '{\n  "format": "duplicate",', 1), "duplicate"),
        )
        with TemporaryDirectory() as directory:
            for index, (rendered, message) in enumerate(mutations):
                with self.subTest(message=message):
                    path = Path(directory) / f"mutant-{index}.json"
                    path.write_text(rendered, encoding="utf-8", newline="\n")
                    with self.assertRaisesRegex(ValueError, message):
                        VERIFIER.verify(path)


if __name__ == "__main__":
    unittest.main()
